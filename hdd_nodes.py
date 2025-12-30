import os
import json
import folder_paths
import re
import pandas as pd
from openai import OpenAI
try: import docx 
except ImportError: docx = None

# 强制关闭代理 (解决 AutoDL 连接阿里云报错)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

# 版本标识: V1.5 - 强制中文标签

# ==============================================================================
# 辅助函数
# ==============================================================================
def clean_json_string(json_str):
    try:
        start = json_str.find('{')
        end = json_str.rfind('}')
        if start != -1 and end != -1:
            return json_str[start:end+1]
        return "{}"
    except: return "{}"

# ==============================================================================
# 节点 1: 剧本角色分析 (HDD_Script_Character_Analysis)
# ==============================================================================
class HDD_Script_Character_Analysis:
    def __init__(self): pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_name": ("STRING", {"default": "请点击下方按钮上传文件...", "multiline": False, "label": "上传剧本文件 (Txt/Docx)"}),
                "model_select": ([
                    "qwen3-max (最新正式版)", 
                    "qwen3-max-preview (思考模式)", 
                    "qwen3-max-2025-09-23 (快照版本)"
                ], {"label": "AI模型选择"}),
                "api_key": ("STRING", {"multiline": False, "default": "", "label": "🔑 阿里云API密钥 (sk-...)"}),
                
                # 测试功能
                "enable_test_mode": ("BOOLEAN", {"default": False, "label": "🛠️ 启用测试模式 (忽略文件，直接测试AI)"}),
                "test_input_text": ("STRING", {"default": "你是谁？", "multiline": True, "label": "测试提问内容"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("角色设定JSON",)
    FUNCTION = "analyze_characters"
    CATEGORY = "HDD/Story"

    def analyze_characters(self, file_name, model_select, api_key, enable_test_mode, test_input_text):
        if not api_key: return ("{}",)
        
        # 模型ID处理
        model_id = "qwen3-max"
        if "preview" in model_select: model_id = "qwen3-max-preview"
        elif "2025-09-23" in model_select: model_id = "qwen3-max-2025-09-23"

        client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

        # --- 测试模式 ---
        if enable_test_mode and test_input_text.strip():
            try:
                print(f"🛠️ [角色分析] 测试模式: {model_id}")
                resp = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": test_input_text}])
                return (resp.choices[0].message.content,)
            except Exception as e: return (json.dumps({"测试错误": str(e)}),)

        # --- 正常逻辑 ---
        input_dir = folder_paths.get_input_directory()
        full_path = os.path.join(input_dir, os.path.basename(file_name))
        if not os.path.exists(full_path): full_path = file_name
        
        text_content = ""
        try:
            if full_path.endswith(('.xlsx', '.xls', '.csv')):
                if full_path.endswith('.csv'): df = pd.read_csv(full_path)
                else: df = pd.read_excel(full_path)
                text_content = df.to_string()
            elif full_path.endswith('.docx'):
                if docx is None: return (json.dumps({"错误": "需安装python-docx库"}),)
                doc = docx.Document(full_path)
                text_content = "\n".join([p.text for p in doc.paragraphs])
            else:
                with open(full_path, 'r', encoding='utf-8') as f: text_content = f.read()
        except Exception as e: return (json.dumps({"错误": str(e)}),)

        system_prompt = """你是一个专业的剧本角色分析师。提取去文本、分镜表格中主要角色的名字和外貌特征，并将其转换成适合Qwen等自然语言的模型的中文提示词，提示词举例“一个有着黑色姬式短发的少女，她有着红色的眼睛，穿着有着复杂花纹的红色日式和服，穿着白袜和褐色短靴”。
要求：输出标准JSON格式，Key为角色名，Value为外貌描述。不要输出Markdown标记。"""

        try:
            resp = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text_content[:30000]}]
            )
            return (clean_json_string(resp.choices[0].message.content),)
        except Exception as e: return (json.dumps({"系统错误": str(e)}),)


# ==============================================================================
# 节点 2: 分镜转绘图 (HDD_Storyboard_Prompt_Gen)
# ==============================================================================
class HDD_Storyboard_Prompt_Gen:
    def __init__(self): pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_name": ("STRING", {"default": "请点击下方按钮上传文件...", "multiline": False, "label": "上传分镜/小说文件"}),
                "input_mode": (["分镜表格模式 (Excel/CSV - 一行一镜)", "小说剧本模式 (Txt/Word - 自动分镜)"], {"label": "输入模式选择"}),
                "model_select": ([
                    "qwen3-max (最新正式版)", 
                    "qwen3-max-preview (思考模式)", 
                    "qwen3-max-2025-09-23 (快照版本)"
                ], {"label": "AI模型选择"}),
                "api_key": ("STRING", {"multiline": False, "default": "", "label": "🔑 阿里云API密钥"}), 
                "style_tag": ([
                    "现代都市", "未来科幻", "古代悬疑", "中式恐怖",
                    "古代唯美", "古风仙侠", "赛博朋克", "末世废土", 
                    "日系校园", "暗黑哥特", "中世纪玄幻", "蒸汽朋克", "克苏鲁神话"
                ], {"label": "画面风格"}),
                "character_config": ("STRING", {"default": "{}", "multiline": True, "label": "角色设定 (手动输入)"}),
                
                # 强制中文标签
                "enable_dialogue": ("BOOLEAN", {"default": True, "label": "启用台词生成"}),
                "enable_sfx": ("BOOLEAN", {"default": False, "label": "启用音效生成"}),
                "enable_camera_move": ("BOOLEAN", {"default": False, "label": "保留运镜描述"}),
                
                # 测试功能
                "enable_test_mode": ("BOOLEAN", {"default": False, "label": "🛠️ 启用测试模式"}),
                "test_input_text": ("STRING", {"default": "你是谁？", "multiline": True, "label": "测试提问内容"}),
            },
            "optional": {
                "external_char_json": ("STRING", {"forceInput": True, "label": "自动角色数据 (连接分析节点)"}),
            }
        }

    RETURN_TYPES = ("STRING", "LIST", "STRING", "STRING")
    RETURN_NAMES = ("完整提示词文本", "提示词列表", "AI思考过程", "API返回原始信息")
    FUNCTION = "process_storyboard"
    CATEGORY = "HDD/Story"

    def process_storyboard(self, file_name, input_mode, model_select, api_key, style_tag, character_config, enable_dialogue, enable_sfx, enable_camera_move, enable_test_mode, test_input_text, external_char_json=None):
        model_id = "qwen3-max"
        if "preview" in model_select: model_id = "qwen3-max-preview"
        elif "2025-09-23" in model_select: model_id = "qwen3-max-2025-09-23"

        # --- 测试模式 ---
        if enable_test_mode and test_input_text.strip():
            print(f"🛠️ [分镜绘图] 测试模式: {model_id}")
            res, thought = self._call_qwen(api_key, model_id, "你是一个有用的助手。", test_input_text)
            return (res, [res], f"思考过程:\n{thought}", f"原始输出: {res}")

        full_thought_process = []
        chars = {}
        try: chars.update(json.loads(character_config))
        except: pass
        if external_char_json and external_char_json.strip():
            try: chars.update(json.loads(clean_json_string(external_char_json)))
            except: pass

        input_dir = folder_paths.get_input_directory()
        clean_name = os.path.basename(file_name)
        full_path = os.path.join(input_dir, clean_name)
        if not os.path.exists(full_path): full_path = file_name 

        raw_content_list = [] 
        if "表格模式" in input_mode:
            try:
                if full_path.endswith(('.xlsx', '.xls')): df = pd.read_excel(full_path)
                elif full_path.endswith('.csv'): df = pd.read_csv(full_path)
                else:
                    with open(full_path, 'r', encoding='utf-8') as f: lines = [l.strip() for l in f.readlines() if l.strip()]
                    df = pd.DataFrame(lines, columns=['Content'])
                for index, row in df.iterrows():
                    row_str = " | ".join([f"{k}: {v}" for k, v in row.items() if pd.notna(v)])
                    raw_content_list.append(row_str)
            except Exception as e: return (f"❌ 表格读取失败: {str(e)}", [], "", f"错误: {str(e)}")
        else:
            novel_text = ""
            try:
                if full_path.endswith('.docx'):
                    if docx is None: return ("❌ 错误：需安装 python-docx", [], "", "")
                    doc = docx.Document(full_path)
                    novel_text = "\n".join([para.text for para in doc.paragraphs])
                else:
                    with open(full_path, 'r', encoding='utf-8') as f: novel_text = f.read()
                
                # 自动分镜
                split_prompt = f"请将以下小说片段拆解成具体的【分镜列表】...\n{novel_text[:3000]}"
                split_res, _ = self._call_qwen(api_key, model_id, "你是一个分镜拆解工具", split_prompt)
                raw_content_list = [line.strip() for line in split_res.split('\n') if line.strip()]
            except Exception as e: return (f"❌ 小说处理失败: {str(e)}", [], "", f"错误: {str(e)}")

        system_instruction = self._build_system_prompt(style_tag, chars, enable_dialogue, enable_sfx, enable_camera_move)
        prompt_results = []
        print(f"🎬 HDD [{model_id}] 开始生成，共 {len(raw_content_list)} 个镜头...")

        for index, content in enumerate(raw_content_list):
            res_text, thought = self._call_qwen(api_key, model_id, system_instruction, content)
            prompt_results.append(res_text)
            if thought: full_thought_process.append(f"--- 镜头 {index+1} ---\n{thought}")

        return ("\n\n".join(prompt_results), prompt_results, "\n\n".join(full_thought_process), "成功")

    def _build_system_prompt(self, style, chars, show_dialogue, show_sfx, show_camera):
        char_rules = "\n".join([f"- 当出现名字【{name}】时，必须替换为视觉描述：{desc}" for name, desc in chars.items()])
        camera_instruction = "5. **保留运镜**: 包含推拉摇移描述。" if show_camera else "5. **去除运镜**: 忽略运镜术语。"
        
        prompt = f"""
你是一个专业的AI动漫分镜转换助手。你的任务是将用户提供的剧情/分镜内容，转化为 Qwen-Image / Midjourney / Flux 可直接使用的中文自然语言提示词，提示词不少于在120-280字。
### 全局设定
- 风格: {style}
- 规则: 绝对去人名化（最终给我的提示词中就算含有人名也得是“名字（外貌描述）”）。例如：小明（一个帅气的年轻男性，黑色短发，黑色耳钉，头顶呆毛，身材强壮，常穿真空黑马甲与紧身西裤，脖子戴松垮领带）表情难过的对着左侧说话。
- 映射表:
{char_rules}
- 内容控制: {"包含台词" if show_dialogue else "不包含台词"}，{"包含音效" if show_sfx else "不包含音效"}
{camera_instruction}
- 光影: 根据分镜描述撰写成具有故事氛围的光影，可以依照“风格基调调整”，并且明确表示晚上/白天/阴天等天气”。
- 场景: 根据分镜上下文理解，每段都要加上场景，场景建筑风格依照“风格基调”。
- 镜头: 根据分镜上下文理解，每段都要加上镜头描述，如：脸部特写镜头/局部特写镜头（明确说明那个部位）/中景镜头/近景镜头/全景/鱼眼镜头等。
- 角度: 根据分镜上下文理解，每段都要加上角色角度，如上一个镜头是正面，那么下一个镜头就得是侧面或者俯视/仰视等其它角度看向另一边或者某个对象，一直一个角度会很怪，根据你的理解以及对镜头的把握来决策。
- 拍摄角度: 根据分镜上下文理解，选择是否加上拍摄角度来加强画面叙事能力，如：俯视拍摄/仰视拍摄等。
- 严禁: 不是特殊情况，角色不能看着镜头（需要说明角色看某个方向，否则ai会自己看向镜头）。
要求：
1. 每一行只输出一个分镜画面描述。
2. 包含角色动作、环境、光影简单描述。
3. 忽略心理描写，转化为视觉画面。
4. 格式：纯文本，每行一个镜头，不要带序号。
直接输出提示词，不要输出思考过程或解释。
"""
        return prompt

    def _call_qwen(self, api_key, model_id, system_prompt, user_content):
        if not api_key: return "错误: 缺少API密钥", ""
        try:
            client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
            resp = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]
            )
            content = resp.choices[0].message.content.strip()
            thought = ""
            try: thought = resp.choices[0].message.reasoning_content
            except: pass
            return content, thought
        except Exception as e: return f"API错误: {str(e)}", ""


# ==============================================================================
# 节点 3: 图生视频提示词 (HDD_Image_to_Video_Prompt_Gen)
# ==============================================================================
class HDD_Image_to_Video_Prompt_Gen:
    def __init__(self): pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enable_batch_mode": ("BOOLEAN", {"default": False, "label": "启用批量模式"}),
                "file_name": ("STRING", {"default": "请点击下方按钮上传文件...", "multiline": False, "label": "上传分镜文件"}),
                "model_select": ([
                    "qwen3-vl-plus (最新正式版)", 
                    "qwen3-vl-plus-2025-12-19 (快照版本)"
                ], {"label": "AI模型选择"}),
                "api_key": ("STRING", {"multiline": False, "default": "", "label": "🔑 阿里云API密钥"}), 
                "style_tag": (["中式恐怖", "古代言情", "现代都市", "古风仙侠", "赛博朋克", "日系二次元", "3D动画"], {"label": "视频风格"}),
                
                # 强制中文标签
                "enable_reasoning": ("BOOLEAN", {"default": False, "label": "显示思考过程"}),
                "enable_sfx": ("BOOLEAN", {"default": False, "label": "生成音效提示"}),
                "enable_bgm": ("BOOLEAN", {"default": False, "label": "生成BGM提示"}),
                "enable_dialogue": ("BOOLEAN", {"default": False, "label": "生成台词提示"}),
                
                # 测试功能
                "enable_test_mode": ("BOOLEAN", {"default": False, "label": "🛠️ 启用测试模式"}),
                "test_input_text": ("STRING", {"default": "描述这张图片？", "multiline": True, "label": "测试提问内容"}),
            },
            "optional": {
                # 单图模式参数
                "input_image": ("IMAGE", {"label": "输入图片 (单图模式)"}),
                "shot_number": ("INT", {"default": 1, "min": 1, "max": 9999, "step": 1, "label": "镜头号 (单图模式)"}),
                # 批量模式参数
                "image_directory": ("STRING", {"default": "/root/autodl-tmp/ComfyUI/output/my_project/", "multiline": False, "label": "图片文件夹路径 (批量模式)"}),
            }
        }

    # 修改点 1: 增加 INT 输出类型
    RETURN_TYPES = ("STRING", "LIST", "STRING", "STRING", "INT")
    # 修改点 2: 增加 "预估时长" 输出名称
    RETURN_NAMES = ("视频提示词", "提示词列表", "AI思考过程", "处理信息", "预估时长")
    FUNCTION = "generate_video_prompt"
    CATEGORY = "HDD/Story"

    def generate_video_prompt(self, enable_batch_mode, file_name, model_select, api_key, style_tag, enable_reasoning, enable_sfx, enable_bgm, enable_dialogue, enable_test_mode, test_input_text, input_image=None, shot_number=1, image_directory=""):
        import base64
        from io import BytesIO
        from PIL import Image, ImageOps
        import numpy as np
        import torch

        if not api_key: return ("错误: 缺少API密钥", [], "", "错误: 缺少API密钥", 5)
        
        # 模型选择
        model_id = "qwen3-vl-plus"
        if "2025-12-19" in model_select: model_id = "qwen3-vl-plus-2025-12-19"
        
        client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        # 思考参数配置
        extra_body = {}
        if enable_reasoning:
            extra_body = {"enable_thinking": True, "thinking_budget": 81920}

        def get_img_base64(img):
            buff = BytesIO()
            img.save(buff, format="JPEG")
            return base64.b64encode(buff.getvalue()).decode("utf-8")
        
        def tensor_to_pil(tensor):
            """将ComfyUI的IMAGE tensor转换为PIL Image"""
            if tensor is None: return None
            # tensor shape: [batch, height, width, channels]
            if len(tensor.shape) == 4:
                tensor = tensor[0]  # 取第一张
            # 转换为numpy并确保值在[0,1]范围
            if tensor.max() > 1.0:
                tensor = tensor / 255.0
            numpy_image = (tensor.cpu().numpy() * 255).astype(np.uint8)
            return Image.fromarray(numpy_image)
        
        # 辅助函数：解析时长
        def parse_duration(text_content):
            try:
                # 匹配 Duration: 5 或 Duration: 10s 等格式
                match = re.search(r"Duration:\s*(\d+)", text_content, re.IGNORECASE)
                if match:
                    val = int(match.group(1))
                    # 限制在 5-12 范围内，防止AI幻觉输出太大或太小的数
                    if val < 5: return 5
                    if val > 12: return 12
                    return val
            except:
                pass
            return 5 # 默认值

        # --- 测试模式 ---
        if enable_test_mode and test_input_text.strip():
            print(f"🛠️ [图生视频] 测试模式: {model_id}")
            try:
                content_payload = [{"type": "text", "text": test_input_text}]
                if input_image is not None:
                    pil_img = tensor_to_pil(input_image)
                    if pil_img:
                        content_payload.insert(0, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{get_img_base64(pil_img)}"}})
                
                resp = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": content_payload}],
                    extra_body=extra_body
                )
                
                thought = ""
                try: thought = resp.choices[0].message.reasoning_content
                except: pass
                
                # 测试模式默认时长返回5
                return (resp.choices[0].message.content, [resp.choices[0].message.content], f"思考过程:\n{thought}", "测试模式完成", 5)
            except Exception as e: return (f"测试错误: {str(e)}", [], "", f"测试错误: {str(e)}", 5)

        # --- 读取分镜表格 ---
        input_dir = folder_paths.get_input_directory()
        full_path = os.path.join(input_dir, os.path.basename(file_name))
        if not os.path.exists(full_path): full_path = file_name 
        
        df = None
        try:
            if full_path.endswith(('.xlsx', '.xls')): df = pd.read_excel(full_path)
            elif full_path.endswith('.csv'): df = pd.read_csv(full_path)
            else: 
                with open(full_path, 'r', encoding='utf-8') as f: lines = [l.strip() for l in f.readlines() if l.strip()]
                df = pd.DataFrame(lines, columns=['Content'])
        except Exception as e: return (f"读取表格错误: {str(e)}", [], "", f"读取表格错误: {str(e)}", 5)
        
        if df is None or len(df) == 0:
            return ("错误: 表格为空或读取失败", [], "", "错误: 表格为空或读取失败", 5)

        # 构建系统提示词
        has_audio_requirement = enable_sfx or enable_bgm or enable_dialogue
        
        sfx_instruction = "要求生成音效提示词 (SFX: ...)。注意：音效不包括台词，只包括环境音、动作音等。" if enable_sfx else "禁止生成任何音效描述。"
        bgm_instruction = "要求根据镜头号和图片的氛围描述合适的BGM。例如：当画面是恐怖氛围时，描述为'悬疑恐怖的二胡音乐'；当画面是紧张氛围时，描述为'紧张刺激的鼓点音乐'等。需要根据画面氛围和剧情需要选择合适的BGM类型和风格。" if enable_bgm else "禁止生成任何背景音乐或BGM描述，并且在最终提示词末尾另起一行加入没有任何背景音乐或BGM的提示词。"
        dialogue_instruction = "要求结合镜号内容和图片内容生成台词提示。分镜脚本中的台词必须原封不动地使用，不要修改台词内容，但可以添加声线描述，例如表格中写着'王年（一个阴沉的青年男性声音）：如果给你一个机会,把家里那位黄脸婆的头换掉...这三款,你会选哪一个?'你就可以整合成'王年（一个阴沉的青年男性声音）愤怒的说道：...'等。需要根据图片中的人物特征和分镜内容判断合适的声线描述,并且最终的台词结构必须是：声线（同一人物固定）＋情绪（变量）：台词内容（变量）。" if enable_dialogue else "禁止生成任何台词相关内容。"
        
        audio_section = f"""
音频要求：
{sfx_instruction}
{bgm_instruction}
{dialogue_instruction}
""" if has_audio_requirement else "音频要求：所有音频功能均已关闭，禁止生成任何音频相关内容（包括音效、BGM、台词等）。"
        
        # 修改点 3: 更新输出格式要求，增加 Duration
        output_format = f"""
输出格式：
- Visual Prompt: (描述画面内容、运镜、具体的动作幅度，中文)
- Duration: (根据画面内容的动作幅度和台词长度，推断所需的视频时长。必须是 5 到 12 之间的整数，单位秒。例如：5, 8, 12)
"""
        if has_audio_requirement:
            output_format += "- Audio Prompt: (包含音效/BGM/台词描述，根据上述要求生成)\n"
        
        sys_prompt = f"""
你是一个AI视频提示词专家。你的任务是根据【输入图片】和【分镜剧本】，生成生成视频模型 (如 Kling, Runway, Vidu) 所需的中文动效提示词和时长预估。
风格: {style_tag}
{audio_section}
请仔细观察图片中的人物、环境、色调，并结合分镜剧本中的动作描述，不需要多余的说明文字，直接给我提示词，方便粘贴复制。
{output_format}
"""

        # --- 单图模式 ---
        if not enable_batch_mode:
            if input_image is None:
                return ("错误: 单图模式需要输入图片", [], "", "错误: 单图模式需要输入图片", 5)
            
            # 转换tensor为PIL Image
            pil_image = tensor_to_pil(input_image)
            if pil_image is None:
                return ("错误: 图片转换失败", [], "", "错误: 图片转换失败", 5)
            
            # 获取对应镜头号的分镜内容
            shot_idx = shot_number - 1  # 镜头号从1开始，索引从0开始
            if shot_idx < 0 or shot_idx >= len(df):
                return (f"错误: 镜头号 {shot_number} 超出范围 (表格共 {len(df)} 行)", [], "", f"错误: 镜头号超出范围", 5)
            
            row_data = df.iloc[shot_idx]
            story_content = " | ".join([f"{k}: {v}" for k, v in row_data.items() if pd.notna(v)])
            
            try:
                img_b64 = get_img_base64(pil_image)
                resp = client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": sys_prompt}, 
                        {"role": "user", "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                            {"type": "text", "text": f"分镜剧本 (镜头{shot_number}): {story_content}"}
                        ]} 
                    ],
                    extra_body=extra_body
                )
                
                content = resp.choices[0].message.content
                thought = ""
                try: thought = resp.choices[0].message.reasoning_content
                except: pass
                
                # 修改点 4: 解析单图时长
                duration_val = parse_duration(content)
                
                return (content, [content], thought, f"成功生成镜头 {shot_number} 的提示词 (时长: {duration_val}s)", duration_val)
            except Exception as e: 
                return (f"API错误: {str(e)}", [], "", f"API错误: {str(e)}", 5)

        # --- 批量模式 ---
        else:
            if not image_directory or not os.path.exists(image_directory):
                return ("错误: 批量模式需要有效的图片文件夹路径", [], "", "错误: 批量模式需要有效的图片文件夹路径", 5)
            
            # 获取所有图片文件
            image_files = sorted([f for f in os.listdir(image_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
            if len(image_files) == 0:
                return ("错误: 图片文件夹中没有找到图片文件", [], "", "错误: 图片文件夹中没有找到图片文件", 5)
            
            # 检查数量匹配
            table_rows = len(df)
            image_count = len(image_files)
            
            if table_rows != image_count:
                return (
                    f"错误: 表格行数 ({table_rows}) 与图片数量 ({image_count}) 不匹配",
                    [],
                    "",
                    f"错误: 表格行数 ({table_rows}) 与图片数量 ({image_count}) 不匹配，请确保数量一致",
                    5
                )
            
            print(f"🎬 HDD [{model_id}] 批量模式: 开始处理 {table_rows} 个镜头...")
            
            all_prompts = []
            all_thoughts = []
            all_durations = [] # 新增时长列表
            error_count = 0
            
            # 逐个处理每个镜头
            for idx in range(table_rows):
                try:
                    # 读取图片
                    img_path = os.path.join(image_directory, image_files[idx])
                    pil_image = Image.open(img_path)
                    pil_image = ImageOps.exif_transpose(pil_image)
                    if pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    # 获取分镜内容
                    row_data = df.iloc[idx]
                    story_content = " | ".join([f"{k}: {v}" for k, v in row_data.items() if pd.notna(v)])
                    
                    # 调用AI
                    img_b64 = get_img_base64(pil_image)
                    resp = client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {"role": "system", "content": sys_prompt}, 
                            {"role": "user", "content": [
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                                {"type": "text", "text": f"分镜剧本 (镜头{idx+1}): {story_content}"}
                            ]} 
                        ],
                        extra_body=extra_body
                    )
                    
                    content = resp.choices[0].message.content
                    all_prompts.append(content)
                    
                    # 解析批量中的时长
                    d_val = parse_duration(content)
                    all_durations.append(d_val)
                    
                    thought = ""
                    try: thought = resp.choices[0].message.reasoning_content
                    except: pass
                    if thought:
                        all_thoughts.append(f"--- 镜头 {idx+1} ---\n{thought}")
                    
                    print(f"✅ 镜头 {idx+1}/{table_rows} 完成 (时长: {d_val}s)")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"镜头 {idx+1} 处理失败: {str(e)}"
                    all_prompts.append(f"错误: {error_msg}")
                    all_durations.append(5) # 错误默认时长
                    print(f"❌ {error_msg}")
            
            # 汇总结果
            combined_thought = "\n\n".join(all_thoughts) if all_thoughts else "无思考过程"
            combined_prompt = "\n\n---\n\n".join(all_prompts)
            info_msg = f"批量处理完成: 成功 {table_rows - error_count}/{table_rows} 个镜头"
            if error_count > 0:
                info_msg += f"，失败 {error_count} 个"
            
            # 注意：最后返回 all_durations (INT LIST)
            return (combined_prompt, all_prompts, combined_thought, info_msg, all_durations)


# ==============================================================================
# 节点 4: 剧本转分镜表格 (HDD_Script_to_Storyboard_Table)
# ==============================================================================
class HDD_Script_to_Storyboard_Table:
    def __init__(self): pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_name": ("STRING", {"default": "请点击下方按钮上传文件...", "multiline": False, "label": "上传剧本/分镜文件"}),
                "input_mode": (["文本剧本模式 (Txt/Word - 自动分镜)", "已有分镜表格模式 (Excel/CSV - 标准化整理)"], {"label": "输入模式选择"}),
                "model_select": ([
                    "qwen3-max (最新正式版)", 
                    "qwen3-max-preview (思考模式)", 
                    "qwen3-max-2025-09-23 (快照版本)"
                ], {"label": "AI模型选择"}),
                "api_key": ("STRING", {"multiline": False, "default": "", "label": "🔑 阿里云API密钥"}),
                "save_path": ("STRING", {"default": "", "multiline": False, "label": "保存路径 (留空使用默认输出目录)"}),
                "output_filename": ("STRING", {"default": "分镜表格_输出.xlsx", "multiline": False, "label": "输出文件名"}),
                
                # 测试功能
                "enable_test_mode": ("BOOLEAN", {"default": False, "label": "🛠️ 启用测试模式"}),
                "test_input_text": ("STRING", {"default": "你是谁？", "multiline": True, "label": "测试提问内容"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("表格文件路径", "表格内容预览")
    FUNCTION = "convert_to_storyboard_table"
    CATEGORY = "HDD/Story"

    def convert_to_storyboard_table(self, file_name, input_mode, model_select, api_key, save_path, output_filename, enable_test_mode, test_input_text):
        if not api_key: return ("", "错误: 缺少API密钥")
        
        # 模型ID处理
        model_id = "qwen3-max"
        if "preview" in model_select: model_id = "qwen3-max-preview"
        elif "2025-09-23" in model_select: model_id = "qwen3-max-2025-09-23"

        client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

        # --- 测试模式 ---
        if enable_test_mode and test_input_text.strip():
            try:
                print(f"🛠️ [分镜表格] 测试模式: {model_id}")
                resp = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": test_input_text}])
                return ("测试模式", resp.choices[0].message.content)
            except Exception as e: return ("", f"测试错误: {str(e)}")

        # --- 读取输入文件 ---
        input_dir = folder_paths.get_input_directory()
        full_path = os.path.join(input_dir, os.path.basename(file_name))
        if not os.path.exists(full_path): full_path = file_name

        input_content = ""
        try:
            if full_path.endswith(('.xlsx', '.xls', '.csv')):
                if full_path.endswith('.csv'): df_input = pd.read_csv(full_path)
                else: df_input = pd.read_excel(full_path)
                input_content = df_input.to_string()
            elif full_path.endswith('.docx'):
                if docx is None: return ("", "错误: 需安装python-docx库")
                doc = docx.Document(full_path)
                input_content = "\n".join([p.text for p in doc.paragraphs])
            else:
                with open(full_path, 'r', encoding='utf-8') as f: input_content = f.read()
        except Exception as e: return ("", f"文件读取错误: {str(e)}")

        # --- 构建AI提示词 ---
        if "文本剧本" in input_mode:
            system_prompt = """你是一个专业的分镜表格生成专家。你的任务是将文本剧本转换为标准化的分镜表格。

输出要求：
1. 必须输出标准的JSON数组格式，每个元素代表一个镜头
2. 每个镜头必须包含以下9个字段（字段名必须完全一致）：
   - "镜号": 数字，从1开始递增
   - "阶段": 如"互动开场"、"转场"、"动机铺垫"、"高潮"、"结尾"等
   - "出场角色": 该镜头中出现的角色名称，多个角色用逗号分隔，并且角色需要增加声线描述
   - "场景": 场景描述，如"一个阴森恐怖的古代书房"、"一个白天的古代街道"等
   - "镜头": 镜头类型，如"单人中景镜头"、"单人侧面脸部特写"、"双人正反打对话镜头"等
   - "画面描述": 详细的画面视觉描述
   - "运镜/动效": 镜头运动或特效描述，如"镜头推近"、"镜头拉远"等，如果没有则填空着
   - "音效/BGM": 音效或背景音乐描述，如"沉闷的心跳声"等，如果没有则空着
   - "台词": 该镜头的对话内容，如果没有则空着

3. 输出格式示例：
[
  {
    "镜号": 1,
    "阶段": "互动开场",
    "出场角色": "你的2D形象（一个阴沉的青年男性声音）",
    "场景": "一个阴森恐怖的古代书房",
    "镜头": "单人中景镜头",
    "画面描述": "【你的2D形象】 中近景。你面前的架子上摆着三颗风格迥异的绝美女性头颅(闭眼)。你的手在上方悬停。",
    "运镜/动效": "镜头推近",
    "音效/BGM": "沉闷的心跳声",
    "台词": "王明（一个阴沉的青年男性声音）：如果给你一个机会,把家里那位黄脸婆的头换掉...这三款,你会选哪一个?"
  }
]

4. 只输出JSON数组，不要输出任何其他文字或Markdown标记。"""
            
            user_prompt = f"请将以下文本剧本转换为标准分镜表格：\n\n{input_content[:20000]}"
        else:
            # 已有分镜表格模式 - 标准化整理
            system_prompt = """你是一个专业的分镜表格标准化专家。你的任务是将已有的分镜表格整理成标准格式。

输出要求：
1. 必须输出标准的JSON数组格式，每个元素代表一个镜头
2. 每个镜头必须包含以下9个字段（字段名必须完全一致）：
   - "镜号": 数字，从1开始递增
   - "阶段": 如"互动开场"、"转场"、"动机铺垫"、"高潮"、"结尾"等
   - "出场角色": 该镜头中出现的角色名称，多个角色用逗号分隔
   - "场景": 场景描述
   - "镜头": 镜头类型描述
   - "画面描述": 详细的画面视觉描述
   - "运镜/动效": 镜头运动或特效描述，如果没有则空着
   - "音效/BGM": 音效或背景音乐描述，如果没有则空着
   - "台词": 该镜头的对话内容，如果没有则填空着

3. 如果输入表格中某些字段缺失，请根据上下文合理推断填充
4. 只输出JSON数组，不要输出任何其他文字或Markdown标记。"""
            
            user_prompt = f"请将以下分镜表格标准化整理：\n\n{input_content[:20000]}"

        # --- 调用AI生成分镜表格 ---
        try:
            print(f"🎬 HDD [{model_id}] 开始生成分镜表格...")
            resp = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            ai_output = resp.choices[0].message.content.strip()
            
            # 清理JSON字符串
            json_start = ai_output.find('[')
            json_end = ai_output.rfind(']')
            if json_start == -1 or json_end == -1:
                return ("", f"AI输出格式错误，未找到JSON数组\n\n原始输出:\n{ai_output}")
            
            json_str = ai_output[json_start:json_end+1]
            storyboard_data = json.loads(json_str)
            
            # --- 转换为DataFrame并保存 ---
            df = pd.DataFrame(storyboard_data)
            
            # 确保列顺序正确
            expected_columns = ["镜号", "阶段", "出场角色", "场景", "镜头", "画面描述", "运镜/动效", "音效/BGM", "台词"]
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = "无"
            df = df[expected_columns]
            
            # 确定保存路径
            if save_path and save_path.strip():
                # 使用自定义路径
                custom_path = save_path.strip()
                if os.path.isdir(custom_path):
                    # 如果是目录，拼接文件名
                    if not output_filename.endswith('.xlsx'):
                        output_filename = output_filename.replace('.csv', '.xlsx').replace('.xls', '.xlsx')
                        if not output_filename.endswith('.xlsx'):
                            output_filename += '.xlsx'
                    import datetime
                    if output_filename == "分镜表格_输出.xlsx" or not any(char.isdigit() for char in output_filename):
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        base_name = output_filename.replace('.xlsx', '')
                        output_filename = f"{base_name}_{timestamp}.xlsx"
                    output_path = os.path.join(custom_path, output_filename)
                else:
                    # 如果是完整文件路径
                    if not custom_path.endswith('.xlsx'):
                        custom_path = custom_path.replace('.csv', '.xlsx').replace('.xls', '.xlsx')
                        if not custom_path.endswith('.xlsx'):
                            custom_path += '.xlsx'
                    output_path = custom_path
                    # 确保目录存在
                    output_dir = os.path.dirname(output_path)
                    if output_dir and not os.path.exists(output_dir):
                        os.makedirs(output_dir, exist_ok=True)
            else:
                # 使用默认输出目录
                output_dir = folder_paths.get_output_directory()
                if not output_filename.endswith('.xlsx'):
                    output_filename = output_filename.replace('.csv', '.xlsx').replace('.xls', '.xlsx')
                    if not output_filename.endswith('.xlsx'):
                        output_filename += '.xlsx'
                
                # 如果文件名不包含时间戳，添加时间戳避免覆盖
                import datetime
                if output_filename == "分镜表格_输出.xlsx" or not any(char.isdigit() for char in output_filename):
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = output_filename.replace('.xlsx', '')
                    output_filename = f"{base_name}_{timestamp}.xlsx"
                
                output_path = os.path.join(output_dir, output_filename)
            
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            # 生成预览文本
            preview_text = f"✅ 成功生成 {len(df)} 个镜头\n\n"
            preview_text += "表格预览（前5行）：\n"
            preview_text += df.head().to_string(index=False)
            
            print(f"✅ 分镜表格已保存: {output_path}")
            return (output_path, preview_text)
            
        except json.JSONDecodeError as e:
            return ("", f"JSON解析错误: {str(e)}\n\nAI输出:\n{ai_output[:500]}")
        except Exception as e:
            return ("", f"处理错误: {str(e)}")