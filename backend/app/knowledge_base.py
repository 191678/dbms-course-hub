from sqlalchemy.orm import Session
from app.models import KnowledgePoint
import json
import base64
import requests

IMAGE_GENERATION_API = "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image"

category_prompts = {
    '基础概念': {
        'prefix': 'Database knowledge infographic about ',
        'suffix': ', flat design style, light green gradient background, blue and green color scheme, clean modern educational illustration, tech diagram with icons and labels, professional visual layout',
        'style': 'technical illustration'
    },
    '关系模型': {
        'prefix': 'Relational database model infographic showing ',
        'suffix': ', entity relationship diagram, table structure visualization, flat design, light green background, blue tables with green accents, clean professional educational infographic, data flow connections',
        'style': 'ER diagram'
    },
    'SQL': {
        'prefix': 'SQL programming educational infographic showing ',
        'suffix': ', code visualization in terminal window, syntax highlighting with color coding, flat design, light green gradient background, clean tech illustration, educational reference style',
        'style': 'code visualization'
    },
    '数据库设计': {
        'prefix': 'Database design infographic for ',
        'suffix': ', ER model diagram, normalization process visualization, flat design style, light green background, blue and green color palette, clean educational diagram, professional layout',
        'style': 'design diagram'
    },
    '安全性': {
        'prefix': 'Database security architecture infographic for ',
        'suffix': ', access control flowchart, encryption layers diagram, flat design, light green gradient background, shield icons, blue and green color scheme, professional security illustration',
        'style': 'security architecture'
    },
    '查询优化': {
        'prefix': 'Query optimization flowchart infographic for ',
        'suffix': ', execution plan visualization, performance analysis diagram, flat design style, light green background, blue and green color scheme, clean technical illustration, educational style',
        'style': 'flowchart'
    },
    '事务': {
        'prefix': 'Transaction processing infographic showing ',
        'suffix': ', ACID properties diagram, isolation levels visualization, transaction lifecycle flow, flat design, light green gradient background, blue green color palette, clean educational illustration',
        'style': 'process diagram'
    },
    '并发控制': {
        'prefix': 'Concurrency control mechanism infographic showing ',
        'suffix': ', locking strategy diagram, MVCC visualization, deadlock prevention flowchart, flat design, light green background, blue and green color scheme, professional technical illustration',
        'style': 'mechanism diagram'
    },
    '索引': {
        'prefix': 'Index data structure infographic for ',
        'suffix': ', B+ tree visualization, indexing strategy diagram, flat design style, light green gradient background, blue tree structure with green nodes, clean educational illustration, professional layout',
        'style': 'data structure'
    }
}

def get_image_prompt(kp: KnowledgePoint) -> str:
    if kp.image_prompt:
        return kp.image_prompt
    
    category = kp.category or '基础概念'
    template = category_prompts.get(category, category_prompts['基础概念'])
    
    content = kp.content.replace('的', ' ').replace('与', ' and ')
    prompt = f"{template['prefix']}{content}{template['suffix']}"
    
    return prompt

async def generate_tts_audio(text: str, voice: str = "zh-CN-XiaoxiaoNeural") -> str:
    try:
        import edge_tts
        import io
        
        communicate = edge_tts.Communicate(text, voice)
        audio_bytes = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes.write(chunk["data"])
        
        audio_base64 = base64.b64encode(audio_bytes.getvalue()).decode("utf-8")
        return f"data:audio/mp3;base64,{audio_base64}"
    
    except Exception as e:
        print(f"[ERROR] TTS generation failed: {str(e)}")
        return ""

def generate_image(prompt: str, image_size: str = "square_hd") -> dict:
    try:
        response = requests.get(
            IMAGE_GENERATION_API,
            params={"prompt": prompt, "image_size": image_size},
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        
        if "json" in content_type.lower():
            try:
                result = response.json()
                if "url" in result:
                    return {"success": True, "image_url": result["url"], "prompt": prompt}
                elif "image_url" in result:
                    return {"success": True, "image_url": result["image_url"], "prompt": prompt}
            except ValueError:
                pass
        
        if "image" in content_type.lower() or \
           response.content[:4] == b"\xff\xd8\xff" or \
           response.content[:2] == b"BM" or \
           response.content[:8] == b"\x89PNG\r\n":
            
            image_base64 = base64.b64encode(response.content).decode("utf-8")
            
            if response.content[:4] == b"\xff\xd8\xff":
                mime_type = "image/jpeg"
            elif response.content[:8] == b"\x89PNG\r\n":
                mime_type = "image/png"
            elif response.content[:2] == b"BM":
                mime_type = "image/bmp"
            else:
                mime_type = content_type or "image/jpeg"
            
            data_url = f"data:{mime_type};base64,{image_base64}"
            return {"success": True, "image_url": data_url, "prompt": prompt}
        
        return {"success": False, "error": f"图片生成失败，返回内容类型: {content_type}"}
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "图片生成超时"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "图片生成服务连接失败"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"图片生成HTTP错误: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"图片生成未知错误: {str(e)}"}

def get_knowledge_from_db(concept: str, db: Session) -> dict:
    kp = db.query(KnowledgePoint).filter(
        KnowledgePoint.content == concept
    ).first()
    if not kp:
        kp = db.query(KnowledgePoint).filter(
            KnowledgePoint.content.like(f"%{concept}%")
        ).first()
    
    if not kp:
        keywords = {
            "关系代数": ["关系代数", "选择", "投影", "笛卡尔积"],
            "SQL优化": ["sql优化", "查询优化", "索引优化"],
            "事务隔离级别": ["事务隔离", "隔离级别"],
            "B+树": ["b+树", "b树"],
            "分布式数据库": ["分布式", "分片"],
            "ACID": ["acid", "原子性", "一致性"],
            "CAP理论": ["cap"],
            "MVCC": ["mvcc"],
            "死锁": ["死锁"],
            "幻读": ["幻读"]
        }
        
        for concept_name, kw_list in keywords.items():
            if any(kw in concept.lower() for kw in kw_list):
                kp = db.query(KnowledgePoint).filter(
                    KnowledgePoint.content.like(f"%{concept_name}%")
                ).first()
                if kp:
                    break
    
    if kp:
        key_points = []
        if kp.key_points:
            try:
                key_points = json.loads(kp.key_points) if isinstance(kp.key_points, str) else kp.key_points
            except:
                pass
        
        result = {
            "success": True,
            "concept": kp.content,
            "definition": kp.detail_content or kp.content,
            "category": kp.category,
            "key_points": key_points,
            "image_prompt": get_image_prompt(kp),
            "video_script": kp.video_script
        }
        return result
    
    return {"success": False, "message": f"暂未找到关于'{concept}'的知识点"}

def generate_video_script(kp: KnowledgePoint) -> dict:
    if kp.video_script:
        lines = [line.strip() for line in kp.video_script.split('\n') if line.strip()]
        steps = []
        for line in lines:
            if line.startswith('步骤'):
                steps.append(line[3:].strip())
            else:
                steps.append(line)
        
        return {
            "success": True,
            "topic": kp.content,
            "duration": f"{len(steps) * 8}秒",
            "steps": steps,
            "description": f"动态演示{kp.content}的动画视频脚本"
        }
    
    return {
        "success": True,
        "topic": kp.content,
        "duration": "30秒",
        "steps": [
            f"步骤1: 介绍{kp.content}",
            f"步骤2: 讲解核心概念",
            f"步骤3: 演示应用场景",
            f"步骤4: 总结要点"
        ],
        "description": f"动态演示{kp.content}的动画视频脚本"
    }
