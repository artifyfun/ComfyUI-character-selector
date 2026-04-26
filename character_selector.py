import json
import os
from server import PromptServer
from aiohttp import web

def get_character_data():
    base_path = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(base_path, "characters.json")
    custom_path = os.path.join(base_path, "characters_custom.json")
    
    all_data = []
    
    # Load base characters
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                all_data.extend(json.load(f))
        except Exception as e:
            print(f"CharacterSelector Error: Failed to load characters.json: {e}")
            
    # Load custom characters
    if os.path.exists(custom_path):
        try:
            with open(custom_path, "r", encoding="utf-8") as f:
                all_data.extend(json.load(f))
        except Exception as e:
            print(f"CharacterSelector Error: Failed to load characters_custom.json: {e}")
            
    return all_data

class CharacterSelectorNode:
    """
    A ComfyUI custom node that allows users to select characters from a JSON file.
    The node outputs character metadata, positive/negative prompts, and LoRA details.
    """
    
    @classmethod
    def INPUT_TYPES(s):
        data = get_character_data()
        names = [char.get("name", "Unknown") for char in data if "name" in char]
        if not names:
            names = ["None"]

        return {
            "required": {
                "character_name": (names, {"default": names[0]}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "FLOAT", "STRING", "STRING", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = (
        "Name",
        "Positive Prompt",
        "Negative Prompt",
        "LoRA 1 Path",
        "LoRA 1 Weight",
        "LoRA 1 Trigger",
        "LoRA 2 Path",
        "LoRA 2 Weight",
        "LoRA 2 Trigger",
        "Source"
    )
    
    FUNCTION = "select_character"
    CATEGORY = "CustomNodes/Character"

    def select_character(self, character_name):
        default_return = ("", "", "", "", 0.0, "", "", 0.0, "", "")
        try:
            data = get_character_data()

            # Find the character by name
            char = next((c for c in data if c.get("name") == character_name), None)

            if char:
                return (
                    str(char.get("name", "")),
                    str(char.get("positive_prompt", "")),
                    str(char.get("negative_prompt", "")),
                    str(char.get("lora1_path", "")),
                    float(char.get("lora1_weight", 0.0)),
                    str(char.get("lora1_trigger", "")),
                    str(char.get("lora2_path", "")),
                    float(char.get("lora2_weight", 0.0)),
                    str(char.get("lora2_trigger", "")),
                    str(char.get("source", ""))
                )
        except Exception as e:
            print(f"CharacterSelector Error: {e}")
            
        return default_return

# Serve character data and images for the preview
@PromptServer.instance.routes.get("/character_selector/get_characters")
async def get_characters(request):
    data = get_character_data()
    return web.json_response(data)

@PromptServer.instance.routes.get("/character_selector/view_cover")
async def view_cover(request):
    filename = request.query.get("filename")
    if not filename:
        return web.Response(status=404)
        
    base_path = os.path.dirname(os.path.realpath(__file__))
    covers_path = os.path.join(base_path, "covers")
    custom_covers_path = os.path.join(base_path, "covers_custom")
    
    # Try custom covers first
    filepath = os.path.join(custom_covers_path, filename)
    if os.path.exists(filepath):
        # Security check
        if os.path.commonpath([custom_covers_path, os.path.abspath(filepath)]) == custom_covers_path:
            return web.FileResponse(filepath)
            
    # Then try base covers
    filepath = os.path.join(covers_path, filename)
    if os.path.exists(filepath):
        # Security check
        if os.path.commonpath([covers_path, os.path.abspath(filepath)]) == covers_path:
            return web.FileResponse(filepath)
            
    return web.Response(status=404)

# Registration mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "CharacterSelector": CharacterSelectorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CharacterSelector": "Character Selector (JSON)"
}
