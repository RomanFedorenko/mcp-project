from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool(
    name="read_doc_content",
    description="Read the content of a document",
)
def read_doc_content(
    doc_id: str = Field(description="ID of the document to read")
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")
    return docs[doc_id]

@mcp.tool(
    name="edit_document",
    description="Edit the content of a document by replacing a string in the documents content with a new string",
)
def edit_document(
    doc_id: str = Field(description="ID of the document that will be edited"),
    old_str: str = Field(description="String to replace. Must match exactly, including whitespace"),
    new_str: str = Field(description="New string to replace with"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return docs[doc_id]

@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())

@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")
    return docs[doc_id]

@mcp.prompt(
    name="format",
    description="Rewrite the content of a document in Markdown format.",
)
def rewrite_doc_in_markdown(doc_id: str = Field(description="ID of the document to format")) -> list[base.Message]:
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")
    prompt = f"""
    You are a world-class document formatter. Your goal is to rewrite the content of the document with markdown syntax.
    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>
    
    Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
    Use the 'edit_document' tool to edit the document. After the document has been reformatted, return the new content.
    """
    return [base.UserMessage(prompt)]

@mcp.prompt(
    name="summarize",
    description="Summarize the content of a document.",
)
def summarize_doc(doc_id: str = Field(description="ID of the document to summarize")) -> list[base.Message]:
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found")
    prompt = f"""
    You are a world-class document summarizer. Your goal is to summarize the content of the document.
    The id of the document you need to summarize is:
    <document_id>
    {doc_id}
    </document_id>
    Use the 'read_doc_content' tool to read the document. After the document has been read, return the summary of the document.
    """
    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
