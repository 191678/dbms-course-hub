from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import KnowledgePoint, Chapter
from app.schemas import KnowledgePointResponse

router = APIRouter()

RELATION_TYPES = {
    'hierarchy': {
        'name': '层级从属',
        'color': '#667eea',
        'lineStyle': 'solid',
        'icon': '↕'
    },
    'causal': {
        'name': '因果关联',
        'color': '#f56c6c',
        'lineStyle': 'dashed',
        'icon': '→'
    },
    'similar': {
        'name': '相似概念',
        'color': '#e6a23c',
        'lineStyle': 'dotted',
        'icon': '≈'
    },
    'derived': {
        'name': '衍生关系',
        'color': '#85ce61',
        'lineStyle': 'dashdot',
        'icon': '⊂'
    }
}

KNOWLEDGE_RELATIONS = {
    '数据模型': {
        'hierarchy': ['层次模型', '网状模型', '关系模型', '概念模型', '逻辑模型', '物理模型'],
        'causal': ['数据库设计', '关系代数'],
        'similar': ['数据结构'],
        'derived': ['ER模型', 'UML']
    },
    '关系模型': {
        'hierarchy': ['关系代数', '关系演算', 'SQL语言'],
        'causal': ['数据库设计范式', '数据依赖'],
        'similar': ['层次模型', '网状模型'],
        'derived': ['关系数据库', 'NoSQL']
    },
    '关系代数': {
        'hierarchy': ['选择运算', '投影运算', '笛卡尔积', '连接运算', '并运算', '差运算', '交运算', '除运算'],
        'causal': ['SQL查询优化'],
        'similar': ['关系演算'],
        'derived': ['查询优化器']
    },
    'SQL语言': {
        'hierarchy': ['数据定义语言', '数据操纵语言', '数据控制语言'],
        'causal': ['数据库安全性', '数据库完整性'],
        'similar': ['关系代数'],
        'derived': ['存储过程', '触发器']
    },
    '数据库设计': {
        'hierarchy': ['需求分析', '概念结构设计', '逻辑结构设计', '物理结构设计'],
        'causal': ['数据模型', '数据库范式'],
        'similar': ['软件工程'],
        'derived': ['ER图设计']
    },
    '数据库范式': {
        'hierarchy': ['第一范式', '第二范式', '第三范式', 'BCNF', '第四范式', '第五范式'],
        'causal': ['数据依赖', '数据库设计'],
        'similar': ['规范化理论'],
        'derived': ['反规范化']
    },
    '数据依赖': {
        'hierarchy': ['函数依赖', '多值依赖', '连接依赖'],
        'causal': ['数据库范式'],
        'similar': ['数据约束'],
        'derived': ['Armstrong公理']
    },
    '事务': {
        'hierarchy': ['事务特性', '事务状态', '事务并发'],
        'causal': ['并发控制', '数据库恢复'],
        'similar': ['进程'],
        'derived': ['分布式事务']
    },
    '并发控制': {
        'hierarchy': ['封锁机制', '并发调度', '隔离级别'],
        'causal': ['死锁', '活锁'],
        'similar': ['操作系统同步'],
        'derived': ['MVCC']
    },
    '死锁': {
        'hierarchy': ['死锁预防', '死锁检测', '死锁解除'],
        'causal': ['并发控制'],
        'similar': ['活锁'],
        'derived': ['死锁避免']
    },
    '数据库恢复': {
        'hierarchy': ['日志恢复', '检查点', '数据库转储'],
        'causal': ['事务', '故障分类'],
        'similar': ['系统备份'],
        'derived': ['灾难恢复']
    },
    '数据库安全性': {
        'hierarchy': ['用户认证', '存取控制', '视图机制', '数据加密', '审计'],
        'causal': ['SQL权限'],
        'similar': ['信息安全'],
        'derived': ['数据库审计']
    },
    '数据库完整性': {
        'hierarchy': ['实体完整性', '参照完整性', '用户定义完整性'],
        'causal': ['约束条件'],
        'similar': ['数据一致性'],
        'derived': ['触发器']
    },
    'B+树索引': {
        'hierarchy': ['索引结构', '索引类型', '索引优化'],
        'causal': ['查询优化', '数据库物理设计'],
        'similar': ['B树', '哈希索引'],
        'derived': ['全文索引']
    },
    '索引': {
        'hierarchy': ['聚集索引', '非聚集索引', '唯一索引', '复合索引'],
        'causal': ['B+树', '查询性能'],
        'similar': ['哈希索引'],
        'derived': ['索引选择']
    },
    'ER图': {
        'hierarchy': ['实体', '属性', '联系', 'ER模型转换'],
        'causal': ['数据库设计', '概念模型'],
        'similar': ['UML类图'],
        'derived': ['关系模式']
    },
    '查询优化': {
        'hierarchy': ['代数优化', '物理优化', '代价估算'],
        'causal': ['关系代数', '索引'],
        'similar': ['编译器优化'],
        'derived': ['执行计划']
    },
    '封锁机制': {
        'hierarchy': ['共享锁', '排他锁', '意向锁', '两段锁协议'],
        'causal': ['并发控制', '死锁'],
        'similar': ['信号量'],
        'derived': ['乐观锁']
    },
    'MVCC': {
        'hierarchy': ['版本链', '读视图', 'undo日志'],
        'causal': ['并发控制', '事务隔离'],
        'similar': ['快照隔离'],
        'derived': ['分布式MVCC']
    },
    '数据模型分类': {
        'hierarchy': ['概念模型', '逻辑模型', '物理模型'],
        'causal': ['数据模型'],
        'similar': ['数据抽象'],
        'derived': ['ER模型']
    },
    '三级模式': {
        'hierarchy': ['外模式', '概念模式', '内模式', '二级映像'],
        'causal': ['数据库系统结构'],
        'similar': ['三层架构'],
        'derived': ['数据独立性']
    },
    '数据库系统概述': {
        'hierarchy': ['数据库系统组成', '数据库管理系统', '数据管理技术'],
        'causal': ['数据模型', '三级模式'],
        'similar': ['信息系统'],
        'derived': ['大数据系统']
    },
}


def find_knowledge_point_by_content(content: str, db: Session) -> Optional[KnowledgePoint]:
    return db.query(KnowledgePoint).filter(KnowledgePoint.content.contains(content)).first()


def find_knowledge_point_by_keyword(keyword: str, db: Session) -> Optional[KnowledgePoint]:
    return db.query(KnowledgePoint).filter(KnowledgePoint.content.like(f"%{keyword}%")).first()


@router.get("/", response_model=dict)
def get_knowledge_graph_root():
    return {
        'success': True,
        'message': '知识图谱API服务正常',
        'endpoints': {
            'relation-types': 'GET /api/knowledge_graph/relation-types/',
            'relations-by-content': 'GET /api/knowledge_graph/relations/by-content/?content=xxx',
            'relations-by-id': 'GET /api/knowledge_graph/relations/{knowledge_point_id}/',
            'knowledge-points-with-relations': 'GET /api/knowledge_graph/knowledge-points/with-relations/'
        }
    }


@router.get("/relations/by-content/", response_model=dict)
def get_knowledge_graph_by_content(content: str, db: Session = Depends(get_db)):
    kp = find_knowledge_point_by_content(content, db)
    if not kp:
        return {
            'success': False,
            'message': '未找到匹配的知识点',
            'nodes': [],
            'edges': [],
            'relation_types': RELATION_TYPES
        }
    return get_knowledge_graph(kp.id, db)


@router.get("/relations/{knowledge_point_id}/", response_model=dict)
def get_knowledge_graph(knowledge_point_id: int, db: Session = Depends(get_db)):
    current_kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == knowledge_point_id).first()
    if not current_kp:
        raise HTTPException(status_code=404, detail="Knowledge point not found")

    relations = {}
    for key in KNOWLEDGE_RELATIONS.keys():
        if key in current_kp.content or current_kp.content in key:
            relations = KNOWLEDGE_RELATIONS[key]
            break

    nodes = []
    edges = []
    node_ids = set()

    nodes.append({
        'id': current_kp.id,
        'label': current_kp.content,
        'category': current_kp.category or '未分类',
        'is_current': True,
        'description': current_kp.detail_content[:200] if current_kp.detail_content else '',
        'difficulty': current_kp.difficulty
    })
    node_ids.add(current_kp.id)

    for relation_type, related_contents in relations.items():
        for keyword in related_contents:
            related_kp = find_knowledge_point_by_keyword(keyword, db)
            if related_kp and related_kp.id not in node_ids:
                nodes.append({
                    'id': related_kp.id,
                    'label': related_kp.content,
                    'category': related_kp.category or '未分类',
                    'is_current': False,
                    'description': related_kp.detail_content[:200] if related_kp.detail_content else '',
                    'difficulty': related_kp.difficulty
                })
                node_ids.add(related_kp.id)
                edges.append({
                    'source': current_kp.id,
                    'target': related_kp.id,
                    'relation_type': relation_type,
                    'relation_name': RELATION_TYPES[relation_type]['name'],
                    'color': RELATION_TYPES[relation_type]['color'],
                    'lineStyle': RELATION_TYPES[relation_type]['lineStyle'],
                    'icon': RELATION_TYPES[relation_type]['icon']
                })

    parent_kp = current_kp.parent
    if parent_kp:
        if parent_kp.id not in node_ids:
            nodes.append({
                'id': parent_kp.id,
                'label': parent_kp.content,
                'category': parent_kp.category or '未分类',
                'is_current': False,
                'description': parent_kp.detail_content[:200] if parent_kp.detail_content else '',
                'difficulty': parent_kp.difficulty
            })
            node_ids.add(parent_kp.id)
        edges.append({
            'source': parent_kp.id,
            'target': current_kp.id,
            'relation_type': 'hierarchy',
            'relation_name': RELATION_TYPES['hierarchy']['name'],
            'color': RELATION_TYPES['hierarchy']['color'],
            'lineStyle': RELATION_TYPES['hierarchy']['lineStyle'],
            'icon': RELATION_TYPES['hierarchy']['icon']
        })

    for child_kp in current_kp.children:
        if child_kp.id not in node_ids:
            nodes.append({
                'id': child_kp.id,
                'label': child_kp.content,
                'category': child_kp.category or '未分类',
                'is_current': False,
                'description': child_kp.detail_content[:200] if child_kp.detail_content else '',
                'difficulty': child_kp.difficulty
            })
            node_ids.add(child_kp.id)
        edges.append({
            'source': current_kp.id,
            'target': child_kp.id,
            'relation_type': 'hierarchy',
            'relation_name': RELATION_TYPES['hierarchy']['name'],
            'color': RELATION_TYPES['hierarchy']['color'],
            'lineStyle': RELATION_TYPES['hierarchy']['lineStyle'],
            'icon': RELATION_TYPES['hierarchy']['icon']
        })

    return {
        'success': True,
        'current_knowledge_point': {
            'id': current_kp.id,
            'label': current_kp.content,
            'category': current_kp.category,
            'description': current_kp.detail_content[:500] if current_kp.detail_content else ''
        },
        'nodes': nodes,
        'edges': edges,
        'relation_types': RELATION_TYPES,
        'total_nodes': len(nodes),
        'total_edges': len(edges)
    }


@router.get("/relation-types/", response_model=dict)
def get_relation_types():
    return RELATION_TYPES


@router.get("/knowledge-points/with-relations/", response_model=list)
def get_all_knowledge_points_with_relations(db: Session = Depends(get_db)):
    kps = db.query(KnowledgePoint).all()
    result = []
    for kp in kps:
        relations = KNOWLEDGE_RELATIONS.get(kp.content, {})
        result.append({
            'id': kp.id,
            'content': kp.content,
            'category': kp.category,
            'parent_id': kp.parent_id,
            'chapter_id': kp.chapter_id,
            'relation_count': sum(len(v) for v in relations.values()) + len(kp.children) + (1 if kp.parent else 0)
        })
    return result
