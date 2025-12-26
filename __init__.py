from .hdd_nodes import HDD_Storyboard_Prompt_Gen, HDD_Image_to_Video_Prompt_Gen, HDD_Script_Character_Analysis, HDD_Script_to_Storyboard_Table

NODE_CLASS_MAPPINGS = {
    "HDD_Storyboard_Prompt_Gen": HDD_Storyboard_Prompt_Gen,
    "HDD_Image_to_Video_Prompt_Gen": HDD_Image_to_Video_Prompt_Gen,
    "HDD_Script_Character_Analysis": HDD_Script_Character_Analysis,
    "HDD_Script_to_Storyboard_Table": HDD_Script_to_Storyboard_Table
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HDD_Storyboard_Prompt_Gen": "HDD🎬 AI漫剧分镜转绘图 V1.5",
    "HDD_Image_to_Video_Prompt_Gen": "HDD🎥 AI漫剧图生视频 V1.5",
    "HDD_Script_Character_Analysis": "HDD👤 AI剧本角色分析 V1.5",
    "HDD_Script_to_Storyboard_Table": "HDD📊 剧本转分镜表格 V1.5"
}

WEB_DIRECTORY = "./js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']