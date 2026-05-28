import os
import json

try:
    from llama_cpp import Llama, LlamaGrammar
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    Llama = None
    LlamaGrammar = None


JSON_GBNF = r"""
root   ::= object
value  ::= object | array | string | number | "true" | "false" | "null"
object ::= "{" ws ( string ws ":" ws value (ws "," ws string ws ":" ws value)* )? ws "}"
array  ::= "[" ws ( value (ws "," ws value)* )? ws "]"
string ::= "\"" ([^"\\\x00-\x1F] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F]{4}))* "\""
number ::= "-"? ("0" | [1-9] [0-9]*) ("." [0-9]+)? ([eE] [-+]? [0-9]+)?
ws     ::= [ \t\n]*
"""

SQL_GBNF = r"""
root            ::= "SELECT " ws column_list ws " FROM " ws table_name ws where_clause ws group_by_clause ws order_by_clause ws limit_clause ws ";"
ws              ::= [ \t\n]*
column_list     ::= column (ws "," ws column)* | "*"
column          ::= identifier | agg_func "(" ws identifier ws ")" | agg_func "(" ws "*" ws ")"
agg_func        ::= "COUNT" | "AVG" | "MAX" | "MIN" | "SUM"
table_name      ::= identifier
where_clause    ::= "" | "WHERE " ws condition
condition       ::= expr (ws logical_op ws expr)*
expr            ::= identifier ws operator ws value | "(" ws condition ws ")"
logical_op      ::= "AND" | "OR"
operator        ::= "=" | "!=" | "<" | ">" | "<=" | ">=" | "LIKE" | "IN" | "IS"
group_by_clause ::= "" | "GROUP BY " ws identifier (ws "," ws identifier)*
order_by_clause ::= "" | "ORDER BY " ws identifier ws ("ASC" | "DESC")?
limit_clause    ::= "" | "LIMIT " ws [0-9]+
identifier      ::= [a-zA-Z_] [a-zA-Z0-9_]*
value           ::= string | number | "NULL" | "TRUE" | "FALSE"
string          ::= "'" [^']* "'"
number          ::= "-"? [0-9]+ ("." [0-9]+)?
"""

class InferenceEngine:
    def __init__(self, model_path="models/llm/qwen2.5-1.5b-instruct-q4_k_m.gguf"):
        if not LLAMA_AVAILABLE:
            raise RuntimeError("LLM dependencies not found. Please run scripts/setup_brain.sh first.")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please run scripts/setup_brain.sh first.")

        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,
            use_mmap=False,
            verbose=False
        )

        self.json_grammar = LlamaGrammar.from_string(JSON_GBNF)
        self.sql_grammar = LlamaGrammar.from_string(SQL_GBNF)

    def stream_generate(self, prompt, max_tokens=512):
        """
        Streams text chunks as they are generated.
        """
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            stream=True
        )
        for chunk in response:
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("text", "")
                if delta:
                    yield delta

    def generate_sql(self, prompt, max_tokens=256):
        """
        Generates and returns a clean SQL string based on the strictly read-only SQL grammar.
        """
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            grammar=self.sql_grammar,
            stream=False
        )
        return response["choices"][0]["text"].strip()

    def generate_json(self, prompt, max_tokens=512):
        """
        Generates JSON according to the grammar and attempts to parse it into a Python dict.
        Returns a fallback dict if parsing fails.
        """
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            grammar=self.json_grammar,
            stream=False
        )
        json_str = response["choices"][0]["text"].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "JSON parse failed", "raw_text": json_str}
