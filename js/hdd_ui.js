import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const hdd_style = `
<style>
    .hdd-modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); z-index: 10000; display: flex; justify-content: center; align-items: center; font-family: 'Segoe UI', sans-serif; backdrop-filter: blur(4px); }
    .hdd-modal-window { background: #0d0d0d; border: 1px solid #00ff9d; width: 850px; height: 600px; display: flex; flex-direction: column; box-shadow: 0 0 30px rgba(0, 255, 157, 0.15); border-radius: 6px; color: #e0e0e0; }
    .hdd-header { padding: 15px 20px; background: #1a1a1a; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
    .hdd-title { font-size: 18px; font-weight: bold; color: #00ff9d; letter-spacing: 1px; }
    .hdd-content { flex: 1; display: flex; overflow: hidden; }
    .hdd-list { width: 240px; border-right: 1px solid #333; overflow-y: auto; background: #111; display: flex; flex-direction: column; }
    .hdd-btn-add { padding: 15px; background: #1a1a1a; color: #00ff9d; border: none; cursor: pointer; border-bottom: 1px solid #333; font-weight: bold; text-align: left; }
    .hdd-btn-add:hover { background: #222; padding-left: 20px; transition: 0.2s; }
    .hdd-char-item { padding: 12px 15px; cursor: pointer; border-bottom: 1px solid #222; transition: 0.2s; font-size: 14px; }
    .hdd-char-item:hover { background: #222; color: #fff; }
    .hdd-char-item.active { background: #00ff9d; color: #000; font-weight: bold; border-left: 4px solid #fff; }
    .hdd-editor { flex: 1; padding: 25px; display: flex; flex-direction: column; gap: 20px; background: #161616;}
    .hdd-input-group { display: flex; flex-direction: column; gap: 8px; }
    .hdd-label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .hdd-input { background: #222; border: 1px solid #444; color: #fff; padding: 12px; border-radius: 4px; outline: none; font-size: 14px; }
    .hdd-input:focus { border-color: #00ff9d; box-shadow: 0 0 5px rgba(0,255,157,0.3); }
    .hdd-textarea { height: 220px; resize: none; line-height: 1.6; }
    .hdd-footer { padding: 15px 20px; border-top: 1px solid #333; background: #1a1a1a; display: flex; justify-content: flex-end; gap: 12px; }
    .hdd-btn { padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 13px; }
    .hdd-btn-cancel { background: #333; color: #aaa; }
    .hdd-btn-save { background: #00ff9d; color: #000; }
    .hdd-btn-del { background: #3a1111; color: #ff6b6b; align-self: flex-start; margin-top: auto; border: 1px solid #521515;}
    .hdd-close-x { background:none; border:none; color:#666; font-size:24px; cursor:pointer; }
    .hdd-close-x:hover { color:#fff; }
</style>
`;

app.registerExtension({
    name: "HDD.StoryboardManager",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const supportedNodes = ["HDD_Storyboard_Prompt_Gen", "HDD_Image_to_Video_Prompt_Gen", "HDD_Script_Character_Analysis", "HDD_Script_to_Storyboard_Table"];
        if (supportedNodes.includes(nodeData.name)) {
            if (!document.getElementById("hdd-style-injected")) {
                document.head.insertAdjacentHTML("beforeend", hdd_style);
                const mark = document.createElement("div"); mark.id = "hdd-style-injected"; document.head.appendChild(mark);
            }
            // 定义所有节点的中文标签映射
            const labelMaps = {
                "HDD_Script_Character_Analysis": {
                    "file_name": "上传剧本文件 (Txt/Docx)",
                    "model_select": "AI模型选择",
                    "api_key": "🔑 阿里云API密钥 (sk-...)",
                    "enable_test_mode": "🛠️ 启用测试模式 (忽略文件，直接测试AI)",
                    "test_input_text": "测试提问内容"
                },
                "HDD_Storyboard_Prompt_Gen": {
                    "file_name": "上传分镜/小说文件",
                    "input_mode": "输入模式选择",
                    "model_select": "AI模型选择",
                    "api_key": "🔑 阿里云API密钥",
                    "style_tag": "画面风格",
                    "character_config": "角色设定 (手动输入)",
                    "enable_dialogue": "启用台词生成",
                    "enable_sfx": "启用音效生成",
                    "enable_camera_move": "保留运镜描述",
                    "enable_test_mode": "🛠️ 启用测试模式",
                    "test_input_text": "测试提问内容",
                    "external_char_json": "自动角色数据 (连接分析节点)"
                },
                "HDD_Image_to_Video_Prompt_Gen": {
                    "enable_batch_mode": "启用批量模式",
                    "file_name": "上传分镜文件",
                    "model_select": "AI模型选择",
                    "api_key": "🔑 阿里云API密钥",
                    "style_tag": "视频风格",
                    "enable_reasoning": "显示思考过程",
                    "enable_sfx": "生成音效提示",
                    "enable_bgm": "生成BGM提示",
                    "enable_dialogue": "生成台词提示",
                    "enable_test_mode": "🛠️ 启用测试模式",
                    "test_input_text": "测试提问内容",
                    "input_image": "输入图片 (单图模式)",
                    "shot_number": "镜头号 (单图模式)",
                    "image_directory": "图片文件夹路径 (批量模式)"
                },
                "HDD_Script_to_Storyboard_Table": {
                    "file_name": "上传剧本/分镜文件",
                    "input_mode": "输入模式选择",
                    "model_select": "AI模型选择",
                    "api_key": "🔑 阿里云API密钥",
                    "save_path": "保存路径 (留空使用默认输出目录)",
                    "output_filename": "输出文件名",
                    "enable_test_mode": "🛠️ 启用测试模式",
                    "test_input_text": "测试提问内容"
                }
            };

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // 设置所有 widget 的中文标签
                const labelMap = labelMaps[nodeData.name];
                if (labelMap) {
                    // 立即设置 widget 的 label 属性
                    this.widgets.forEach(widget => {
                        if (widget.name && labelMap[widget.name]) {
                            widget.label = labelMap[widget.name];
                        }
                    });
                    
                    // 延迟更新 DOM 标签文本
                    const updateLabels = () => {
                        if (!this.domAt) return;
                        const nodeEl = this.domAt;
                        
                        this.widgets.forEach(widget => {
                            if (widget.name && labelMap[widget.name]) {
                                // 查找所有可能的标签位置
                                const selectors = [
                                    `.property-widget:has([name="${widget.name}"]) .widget-label`,
                                    `.property-widget:has([name="${widget.name}"]) .widget_header`,
                                    `label[for="${widget.name}"]`,
                                    `[data-widget-name="${widget.name}"] .widget-label`
                                ];
                                
                                let labelEl = null;
                                for (const selector of selectors) {
                                    try {
                                        labelEl = nodeEl.querySelector(selector);
                                        if (labelEl) break;
                                    } catch(e) {}
                                }
                                
                                // 如果选择器找不到，手动查找
                                if (!labelEl) {
                                    const widgetContainer = Array.from(nodeEl.querySelectorAll('.property-widget')).find(el => {
                                        const input = el.querySelector(`[name="${widget.name}"], [id="${widget.name}"]`);
                                        return input !== null;
                                    });
                                    if (widgetContainer) {
                                        labelEl = widgetContainer.querySelector('.widget-label, .widget_header, label') ||
                                                 widgetContainer.previousElementSibling;
                                    }
                                }
                                
                                if (labelEl) {
                                    labelEl.textContent = labelMap[widget.name];
                                }
                            }
                        });
                    };
                    
                    // 多次尝试更新，确保 DOM 已渲染
                    setTimeout(updateLabels, 50);
                    setTimeout(updateLabels, 200);
                    setTimeout(updateLabels, 500);
                }
                
                if (nodeData.name === "HDD_Storyboard_Prompt_Gen") {
                    const configWidget = this.widgets.find(w => w.name === "character_config");
                    if (configWidget) configWidget.type = "hidden";
                    this.addWidget("button", "👥 打开角色设定面板", null, () => { this.openCharacterManager(configWidget); });
                }
                const fileWidget = this.widgets.find(w => w.name === "file_name");
                if (fileWidget) {
                    this.addWidget("button", "📂 点击上传文件", null, () => {
                        const fileInput = document.createElement("input");
                        fileInput.type = "file";
                        fileInput.accept = ".xlsx,.xls,.csv,.txt,.docx";
                        fileInput.style.display = "none";
                        fileInput.onchange = async () => {
                            if (fileInput.files.length > 0) {
                                const file = fileInput.files[0];
                                const formData = new FormData();
                                formData.append("image", file);
                                formData.append("overwrite", "true");
                                try {
                                    const resp = await api.fetchApi("/upload/image", { method: "POST", body: formData });
                                    if (resp.status === 200) {
                                        const data = await resp.json();
                                        fileWidget.value = data.name;
                                        alert(`✅ 上传成功: ${data.name}`);
                                    } else { alert(`❌ 上传失败: ${resp.statusText}`); }
                                } catch (err) { alert(`❌ 上传出错: ${err}`); }
                            }
                        };
                        document.body.appendChild(fileInput);
                        fileInput.click();
                        document.body.removeChild(fileInput);
                    });
                }
                return r;
            };
            nodeType.prototype.openCharacterManager = function(targetWidget) {
                let charData = {};
                try { charData = JSON.parse(targetWidget.value || "{}"); } catch(e) { charData = {}; }
                let chars = Object.keys(charData).map(key => ({ name: key, desc: charData[key] }));
                let activeIndex = chars.length > 0 ? 0 : -1;
                const overlay = document.createElement("div"); overlay.className = "hdd-modal-overlay";
                const modal = document.createElement("div"); modal.className = "hdd-modal-window";
                const render = () => {
                    const activeChar = activeIndex >= 0 ? chars[activeIndex] : null;
                    modal.innerHTML = `
                        <div class="hdd-header"><span class="hdd-title">HDD 角色设定</span><button class="hdd-close-x" id="hdd-close">×</button></div>
                        <div class="hdd-content">
                            <div class="hdd-list">
                                <button class="hdd-btn-add" id="hdd-add">+ 新建角色</button>
                                <div id="hdd-char-list-container">${chars.map((c, i) => `<div class="hdd-char-item ${i === activeIndex ? 'active' : ''}" data-index="${i}">${c.name || "未命名"}</div>`).join('')}</div>
                            </div>
                            <div class="hdd-editor">
                                ${activeChar ? `
                                    <div class="hdd-input-group"><label class="hdd-label">角色名</label><input class="hdd-input" id="hdd-input-name" value="${activeChar.name}"></div>
                                    <div class="hdd-input-group"><label class="hdd-label">外貌描述</label><textarea class="hdd-input hdd-textarea" id="hdd-input-desc">${activeChar.desc}</textarea></div>
                                    <button class="hdd-btn hdd-btn-del" id="hdd-del">🗑️ 删除</button>
                                ` : '<div style="color:#666;display:flex;justify-content:center;align-items:center;height:100%;">请选择或新建角色</div>'}
                            </div>
                        </div>
                        <div class="hdd-footer"><button class="hdd-btn hdd-btn-cancel" id="hdd-cancel">取消</button><button class="hdd-btn hdd-btn-save" id="hdd-save">保存</button></div>
                    `;
                    modal.querySelectorAll('.hdd-char-item').forEach(el => { el.onclick = () => { saveCurrent(); activeIndex = parseInt(el.dataset.index); render(); }; });
                    const add = modal.querySelector('#hdd-add'); if(add) add.onclick=()=>{ saveCurrent(); chars.push({name:"新角色",desc:""}); activeIndex=chars.length-1; render(); };
                    const del = modal.querySelector('#hdd-del'); if(del) del.onclick=()=>{ if(confirm("删除?")){ chars.splice(activeIndex,1); activeIndex=Math.max(0,activeIndex-1); if(chars.length===0)activeIndex=-1; render(); }};
                    modal.querySelector('#hdd-close').onclick=()=>document.body.removeChild(overlay);
                    modal.querySelector('#hdd-cancel').onclick=()=>document.body.removeChild(overlay);
                    modal.querySelector('#hdd-save').onclick=()=>{ saveCurrent(); const final={}; chars.forEach(c=>{if(c.name.trim())final[c.name.trim()]=c.desc.trim();}); targetWidget.value=JSON.stringify(final,null,2); if(targetWidget.callback)targetWidget.callback(targetWidget.value); document.body.removeChild(overlay); };
                    function saveCurrent(){ if(activeIndex>=0 && chars[activeIndex]){ const n=document.getElementById('hdd-input-name'), d=document.getElementById('hdd-input-desc'); if(n)chars[activeIndex].name=n.value; if(d)chars[activeIndex].desc=d.value; }}
                };
                overlay.appendChild(modal); document.body.appendChild(overlay); render();
            };
        }
    }
});