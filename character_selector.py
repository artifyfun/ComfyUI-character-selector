import json
import os
from server import PromptServer
from aiohttp import web

class CharacterSelectorNode:
    """
    A ComfyUI custom node that allows users to select characters from a JSON file.
    The node outputs character metadata, positive/negative prompts, and LoRA details.
    """
    
    @classmethod
    def INPUT_TYPES(s):
        # Locate the JSON file in the same directory as the script
        json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "characters.json")
        
        names = ["None"]
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    names = [char.get("name", "Unknown") for char in data if "name" in char]
            except Exception as e:
                print(f"CharacterSelector Error: Failed to load characters.json: {e}")
        else:
            print(f"CharacterSelector Warning: characters.json not found at {json_path}")

        return {
            "required": {
                "character_name": (names, {"default": names[0]}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "FLOAT", "STRING", "STRING", "FLOAT", "STRING")
    RETURN_NAMES = (
        "Name", 
        "Positive Prompt", 
        "Negative Prompt", 
        "LoRA 1 Path", 
        "LoRA 1 Weight", 
        "LoRA 1 Trigger", 
        "LoRA 2 Path", 
        "LoRA 2 Weight", 
        "LoRA 2 Trigger"
    )
    
    FUNCTION = "select_character"
    CATEGORY = "CustomNodes/Character"

    def select_character(self, character_name):
        json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "characters.json")
        
        default_return = ("", "", "", "", 0.0, "", "", 0.0, "")
        
        if not os.path.exists(json_path):
            return default_return
            
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
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
                    str(char.get("lora2_trigger", ""))
                )
                
        except Exception as e:
            print(f"CharacterSelector Error: {e}")
            
        return default_return

# Serve character data and images for the preview
@PromptServer.instance.routes.get("/character_selector/get_characters")
async def get_characters(request):
    json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "characters.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return web.json_response(data)
    return web.json_response([])

@PromptServer.instance.routes.get("/character_selector/view_cover")
async def view_cover(request):
    filename = request.query.get("filename")
    if not filename:
        return web.Response(status=404)
        
    covers_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "covers")
    filepath = os.path.join(covers_path, filename)
    
    # Simple security check to stay within covers directory
    if os.path.commonpath([covers_path, os.path.abspath(filepath)]) != covers_path:
        return web.Response(status=403)
        
    if os.path.exists(filepath):
        return web.FileResponse(filepath)
    return web.Response(status=404)

# Registration mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "CharacterSelector": CharacterSelectorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CharacterSelector": "Character Selector (JSON)"
}
