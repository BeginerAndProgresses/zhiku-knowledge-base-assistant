from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch


def get_model(model_name=None):
    """
    获取本地模型实例
    如果没有指定模型名称，则使用默认配置
    """
    if model_name is None:
        # 这里可以设置一个默认的本地模型路径
        model_name = r"D:\code\model\model_store\default_model"  # 修改为你的实际模型路径
    
    try:
        # 加载模型和分词器
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # 创建文本生成pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            temperature=0.7,
            repetition_penalty=1.1
        )
        
        # 返回LangChain包装的模型
        hf_pipeline = HuggingFacePipeline(pipeline=pipe)
        return hf_pipeline
        
    except Exception as e:
        print(f"加载模型时出错: {e}")
        print("请确保已正确安装transformers和torch库")
        print("如果缺少依赖，请运行: pip install torch transformers")
        return None