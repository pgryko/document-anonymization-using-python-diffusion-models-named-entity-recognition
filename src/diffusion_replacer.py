"""
Diffusion model-based text replacer for anonymizing sensitive information.
"""
from typing import Dict, List, Union, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from diffusers import StableDiffusionPipeline

class DiffusionReplacer:
    """
    Class that uses diffusion models to replace sensitive text 
    with plausible but fake information.
    """
    
    def __init__(
        self, 
        text_model_name: str = "gpt2",
        diffusion_model_name: str = "runwayml/stable-diffusion-v1-5",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize the diffusion replacer with language and diffusion models.
        
        Args:
            text_model_name: The transformer model to use for text generation
            diffusion_model_name: The diffusion model to use for image generation
            device: The device to use for inference (cuda or cpu)
        """
        self.device = device
        
        # Load text generation model
        self.tokenizer = AutoTokenizer.from_pretrained(text_model_name)
        self.text_model = AutoModelForCausalLM.from_pretrained(text_model_name)
        self.text_model.to(self.device)
        
        # Load diffusion model for image generation (if needed)
        self.diffusion_model = None
        self.diffusion_model_name = diffusion_model_name
    
    def load_diffusion_model(self):
        """
        Load the diffusion model on demand to save memory when not using image generation.
        """
        if self.diffusion_model is None:
            self.diffusion_model = StableDiffusionPipeline.from_pretrained(
                self.diffusion_model_name, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.diffusion_model.to(self.device)
    
    def replace_text(
        self, 
        text: str, 
        entity_type: str, 
        max_length: int = 50,
        temperature: float = 0.7
    ) -> str:
        """
        Replace sensitive text with generated fake text of the same entity type.
        
        Args:
            text: The original sensitive text to replace
            entity_type: The type of entity (PERSON, ORG, etc.)
            max_length: Maximum length of generated text
            temperature: Sampling temperature (higher = more random)
            
        Returns:
            A string containing the generated replacement text
        """
        # Create appropriate prompt based on entity type
        if entity_type == "PERSON":
            prompt = f"Generate a fictional person's name to replace '{text}':"
        elif entity_type == "ORG":
            prompt = f"Generate a fictional organization name to replace '{text}':"
        elif entity_type == "GPE" or entity_type == "LOC":
            prompt = f"Generate a fictional location name to replace '{text}':"
        elif entity_type == "MONEY":
            prompt = f"Generate a fictional money amount to replace '{text}':"
        elif entity_type == "DATE":
            prompt = f"Generate a fictional date to replace '{text}':"
        else:
            prompt = f"Generate fictional text to replace '{text}':"
        
        # Tokenize the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        # Generate replacement text
        with torch.no_grad():
            outputs = self.text_model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=len(inputs["input_ids"][0]) + max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.95
            )
        
        # Decode the generated text
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the generated part (remove the prompt)
        replacement = generated_text[len(prompt):].strip()
        
        # If nothing was generated or the generation is empty, return a default
        if not replacement:
            if entity_type == "PERSON":
                return "John Doe"
            elif entity_type == "ORG":
                return "Example Corporation"
            elif entity_type == "GPE" or entity_type == "LOC":
                return "Springfield"
            elif entity_type == "MONEY":
                return "$100.00"
            elif entity_type == "DATE":
                return "January 1, 2023"
            else:
                return "[REDACTED]"
        
        return replacement
    
    def generate_replacement_image(
        self, 
        prompt: str,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5
    ):
        """
        Generate a replacement image using the diffusion model.
        
        Args:
            prompt: Text prompt for the image generation
            width: Width of the generated image
            height: Height of the generated image
            num_inference_steps: Number of denoising steps
            guidance_scale: Scale for classifier-free guidance
            
        Returns:
            A PIL Image object
        """
        # Lazy-load the diffusion model when first needed
        self.load_diffusion_model()
        
        # Generate the image
        with torch.no_grad():
            image = self.diffusion_model(
                prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            ).images[0]
        
        return image
    
    def replace_entities_in_text(
        self, 
        text: str, 
        entities: List[Dict]
    ) -> str:
        """
        Replace all detected entities in a text with generated replacements.
        
        Args:
            text: The original text containing sensitive information
            entities: A list of entity dictionaries with text, label, start_char, end_char
            
        Returns:
            The text with sensitive entities replaced
        """
        # Sort entities by start_char in reverse order to avoid position shifts
        sorted_entities = sorted(entities, key=lambda x: x["start_char"], reverse=True)
        
        # Create a mutable list of characters from the text
        chars = list(text)
        
        # Keep track of used replacements to maintain consistency
        replacement_map = {}
        
        # Replace each entity
        for entity in sorted_entities:
            original_text = entity["text"]
            entity_type = entity["label"]
            start = entity["start_char"]
            end = entity["end_char"]
            
            # Check if we've already replaced this text (for consistency)
            if original_text in replacement_map:
                replacement = replacement_map[original_text]
            else:
                replacement = self.replace_text(original_text, entity_type)
                replacement_map[original_text] = replacement
            
            # Replace the characters in the list
            chars[start:end] = list(replacement)
        
        # Join the characters back into a string
        return "".join(chars)