import pandas as pd
import random

# 生成单选题
def generate_single_questions(count):
    questions = []
    subjects = ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '计算机']
    options = ['A', 'B', 'C', 'D']
    
    for i in range(count):
        subject = random.choice(subjects)
        question_num = random.randint(1, 100)
        answer = random.choice(options)
        
        question = {
            'type': 'single',
            'content': f'{subject}第{question_num}题：下列关于{subject}的说法，正确的是？',
            'options': '{"A": "选项A内容", "B": "选项B内容", "C": "选项C内容", "D": "选项D内容"}',
            'answer': answer,
            'score': 2,
            'analysis': f'{subject}相关知识解析，正确答案为{answer}。',
            'difficulty': random.randint(1, 5),
            'chapter': f'{subject}第{random.randint(1, 10)}章',
            'knowledge_point': f'{subject}知识点{random.randint(1, 50)}'
        }
        questions.append(question)
    return questions

# 生成多选题
def generate_multiple_questions(count):
    questions = []
    subjects = ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '计算机']
    
    for i in range(count):
        subject = random.choice(subjects)
        question_num = random.randint(1, 100)
        
        # 随机生成2-4个正确答案
        answers = random.sample(['A', 'B', 'C', 'D'], random.randint(2, 4))
        answer_str = ','.join(sorted(answers))
        
        question = {
            'type': 'multiple',
            'content': f'{subject}第{question_num}题：下列关于{subject}的说法，正确的有？（多选）',
            'options': '{"A": "选项A内容", "B": "选项B内容", "C": "选项C内容", "D": "选项D内容"}',
            'answer': answer_str,
            'score': 4,
            'analysis': f'{subject}相关知识解析，正确答案为{answer_str}。',
            'difficulty': random.randint(3, 5),
            'chapter': f'{subject}第{random.randint(1, 10)}章',
            'knowledge_point': f'{subject}知识点{random.randint(1, 50)}'
        }
        questions.append(question)
    return questions

# 生成判断题
def generate_judge_questions(count):
    questions = []
    subjects = ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '计算机']
    
    for i in range(count):
        subject = random.choice(subjects)
        question_num = random.randint(1, 100)
        answer = random.choice(['对', '错'])
        
        question = {
            'type': 'judge',
            'content': f'{subject}第{question_num}题：{subject}中某个重要定理或概念的陈述是否正确？',
            'options': '',
            'answer': answer,
            'score': 1,
            'analysis': f'{subject}相关知识解析，本题答案为{answer}。',
            'difficulty': random.randint(1, 4),
            'chapter': f'{subject}第{random.randint(1, 10)}章',
            'knowledge_point': f'{subject}知识点{random.randint(1, 50)}'
        }
        questions.append(question)
    return questions

# 生成填空题
def generate_fill_questions(count):
    questions = []
    subjects = ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '计算机']
    
    for i in range(count):
        subject = random.choice(subjects)
        question_num = random.randint(1, 100)
        
        question = {
            'type': 'fill',
            'content': f'{subject}第{question_num}题：{subject}中，______是重要的概念，它的定义是______。',
            'options': '',
            'answer': f'答案1;答案2',
            'score': 3,
            'analysis': f'{subject}相关知识解析。',
            'difficulty': random.randint(2, 4),
            'chapter': f'{subject}第{random.randint(1, 10)}章',
            'knowledge_point': f'{subject}知识点{random.randint(1, 50)}'
        }
        questions.append(question)
    return questions

# 生成简答题
def generate_essay_questions(count):
    questions = []
    subjects = ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治', '计算机']
    
    for i in range(count):
        subject = random.choice(subjects)
        question_num = random.randint(1, 100)
        
        question = {
            'type': 'essay',
            'content': f'{subject}第{question_num}题：请简述{subject}中某个重要概念的定义及其应用。',
            'options': '',
            'answer': f'{subject}相关知识的详细解答，包括定义、特点、应用等方面。',
            'score': 10,
            'analysis': f'{subject}相关知识解析，本题考查学生对{subject}核心概念的理解。',
            'difficulty': random.randint(3, 5),
            'chapter': f'{subject}第{random.randint(1, 10)}章',
            'knowledge_point': f'{subject}知识点{random.randint(1, 50)}'
        }
        questions.append(question)
    return questions

# 生成论述题
def generate_discussion_questions(count):
    questions = []
    subjects = ['语文', '历史', '地理', '政治', '生物']
    
    for i in range(count):
        subject = random.choice(subjects)
        question_num = random.randint(1, 100)
        
        question = {
            'type': 'discussion',
            'content': f'{subject}第{question_num}题：请结合实际，论述{subject}中某个重要理论或观点的意义和影响。',
            'options': '',
            'answer': f'{subject}相关理论的详细论述，包括理论概述、实际应用、意义分析等。',
            'score': 15,
            'analysis': f'{subject}相关知识解析，本题考查学生综合分析和论述能力。',
            'difficulty': 5,
            'chapter': f'{subject}第{random.randint(1, 10)}章',
            'knowledge_point': f'{subject}知识点{random.randint(1, 50)}'
        }
        questions.append(question)
    return questions

# 主函数
def main():
    # 各类题型数量分配（总计100题）
    question_counts = {
        'single': 30,    # 单选题 30题
        'multiple': 20,  # 多选题 20题
        'judge': 20,     # 判断题 20题
        'fill': 15,      # 填空题 15题
        'essay': 10,     # 简答题 10题
        'discussion': 5  # 论述题 5题
    }
    
    # 生成所有题目
    all_questions = []
    all_questions.extend(generate_single_questions(question_counts['single']))
    all_questions.extend(generate_multiple_questions(question_counts['multiple']))
    all_questions.extend(generate_judge_questions(question_counts['judge']))
    all_questions.extend(generate_fill_questions(question_counts['fill']))
    all_questions.extend(generate_essay_questions(question_counts['essay']))
    all_questions.extend(generate_discussion_questions(question_counts['discussion']))
    
    # 打乱顺序
    random.shuffle(all_questions)
    
    # 创建DataFrame
    df = pd.DataFrame(all_questions)
    
    # 保存为Excel文件
    output_path = 'question_bank/questions_100.xlsx'
    df.to_excel(output_path, index=False)
    
    print(f'成功生成{len(all_questions)}道试题，已保存到 {output_path}')
    print(f'\n题型分布：')
    for q_type, count in question_counts.items():
        print(f'  {q_type}: {count}题')

if __name__ == '__main__':
    main()
