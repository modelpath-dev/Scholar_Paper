import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import ConceptNode

# Load environment variables from .env
load_dotenv()

# Initialize the OpenAI model
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=api_key,
    temperature=0.1
)

def generate_concept_tree(text: str) -> ConceptNode:
    """
    Sends section text to Gemini to extract a structured hierarchical concept tree.
    """
    system_prompt = (
        "You are a scientific analyst. Your task is to convert the provided research paper text "
        "into a structured JSON tree of concepts. \n"
        "Level 1: Main Method or Topic\n"
        "Level 2: Sub-components, algorithms, or theories\n"
        "Level 3: Key details, parameters, or specific findings.\n\n"
        "The output must be a valid JSON object matching this structure:\n"
        "{{\n"
        "  \"id\": \"unique_id\",\n"
        "  \"label\": \"Concept Name\",\n"
        "  \"summary\": \"Brief summary of the concept\",\n"
        "  \"children\": [\n"
        "    {{ ... sub-concepts ... }}\n"
        "  ]\n"
        "}}\n"
        "Only output the JSON. Do not include any markdown formatting or explanation."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Extracted text: \n\n{text}")
    ])

    # Run the chain
    chain = prompt | llm
    
    response = chain.invoke({"text": text})
    
    # Strip potential markdown formatting if Gemini includes it
    content = response.content.strip()
    if content.startswith("```json"):
        content = content.replace("```json", "").replace("```", "").strip()
    
    try:
        data = json.loads(content)
        # Parse into Pydantic model to validate and handle recursive children
        return ConceptNode.model_validate(data)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw response: {content}")
        raise ValueError(f"Failed to generate valid concept tree: {e}")

if __name__ == "__main__":
    # Test logic
    sample_text = "This paper introduces the Transformer architecture. It relies on Attention mechanisms, specifically Self-Attention and Multi-Head Attention. The Multi-Head Attention allows the model to attend to different parts of the sequence simultaneously."
    try:
        tree = generate_concept_tree(sample_text)
        print(tree.model_dump_json(indent=2))
    except Exception as e:
        print(f"Test failed: {e}")
