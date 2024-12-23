from dataclasses import dataclass
from typing import Dict, Literal, Optional
import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

PY_LANGUAGE = Language(tspython.language())

@dataclass
class EmptyNode:
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    type: str = "empty"
    parent: None = None

class FileContext:
    """Tree of context for a single source code file. Show nodes using the `show` method."""
    def __init__(self, file: str):
        self.file = file
        with open(file, 'r') as f:
            self.code = f.read()
        self.lines = self.code.splitlines()
        self.tree = Parser(PY_LANGUAGE).parse(bytes(self.code, "utf8"))
        self.root_node = self.tree.root_node
        self.show_indices = set()
        self.comments: Dict[int, str] = {}
        self.nodes = [[] for _ in range(len(self.lines) + 1)]
        self.scopes = [set() for _ in range(len(self.lines) + 1)]
        self.walk_tree(self.root_node)

    def function_query(self, name: Optional[str] = None):
        return f"(function_definition name: (identifier) @name.definition.function{f" (#match? @name.definition.function \"{name}\")" if name else ""}) @definition.function"

    def class_query(self, name: Optional[str] = None):
        return f"(class_definition name: (identifier) @name.definition.class {f" (#match? @name.definition.class \"{name}\")" if name else ""}) @definition.class"

    def assignment_query(self, name: Optional[str] = None):
        return f"(assignment left: (identifier) @name.definition.variable {f" (#match? @name.definition.variable \"{name}\")" if name else ""}) @definition.variable"
    
    def definition_query(self, name: Optional[str] = None):
        return f"{self.function_query(name)}\n{self.class_query(name)}\n{self.assignment_query(name)}"

    def import_query(self):
        return "(import_statement (dotted_name) @name.definition.import)\n(import_from_statement (dotted_name) @name.definition.import)"

    def is_definition(self, node: Node):
        return node.type in ["function_definition", "class_definition", "assignment"]

    def nearest_definition_node(self, node: Node):
        if self.is_definition(node) or node.type == "empty": return node
        parent = node.parent
        while parent and not self.is_definition(parent): parent = parent.parent
        return parent or node
    
    def find_all_children(self, node):
        children = [node]
        for child in node.children:
            children += self.find_all_children(child)
        return children
    
    def node_for_line(self, line: int, definition: bool = False):
        if not self.lines[line - 1].strip(): return EmptyNode(start_point=(line - 1, 0), end_point=(line - 1, 0))
        smallest = None
        def size(node: Optional[Node]): return (node.end_point[0] - node.start_point[0]) if node else float("inf")
        def in_range(node: Optional[Node]): return node.start_point[0] <= line - 1 and node.end_point[0] >= line - 1
        for node_list in self.nodes:
            for node in node_list:
                if in_range(node) and (size(node) < size(smallest)) and (not definition or self.is_definition(node)):
                    smallest = node
        return smallest or EmptyNode(start_point=(line - 1, 0), end_point=(line - 1, 0))
        
    def query(self, query_string: str):
        query = PY_LANGUAGE.query(query_string)
        captures = query.captures(self.tree.root_node)
        return [node for _, nodes in captures.items() for node in nodes]

    def preprocess_names(self, names: list[str]):
        output = []
        for name in names:
            output += name.split(".") # support class.method queries
            output.append(name) # include just in case
        return output
    
    def show(
        self,
        line_range: Optional[tuple[int, int]] = None,
        lines: Optional[list[int]] = None,
        query: Optional[str] = None,
        names: Optional[list[str]] = None,
        scope: Literal["full", "line", "partial"] = "line",
        parents: Literal["none", "all"] = "none",
        last_line: bool = True,
    ):
        if lines:
            # force full scope and nearest definition node - after a fuzzy search or RAG
            # the agent may expand the context around a line like a docstring which
            # doesn't give it proper context so just default to showing the entire function
            nodes = [self.node_for_line(line, definition = True) for line in lines]
            self.show_indices.update([l - 1 for l in lines])
        elif query: nodes = self.query(query)
        elif names: nodes = self.query(self.definition_query("|".join(self.preprocess_names(names))))
        elif line_range:
            if line_range[1] == -1: line_range = (line_range[0], len(self.lines) - 1)
            if line_range[0] == -1: line_range = (len(self.lines) - 1, line_range[1])
            nodes = [self.node_for_line(line) for line in range(line_range[0], line_range[1] + 1)]
            self.show_indices.update(range(line_range[0] -1, line_range[1]))
            # scope = "full"
        else: print("No line, name or definition provided"); return self
        for node in nodes:
            if scope == "full": self.show_indices.update(range(node.start_point[0], node.end_point[0] + 1))
            elif scope == "line": self.show_indices.add(node.start_point[0])
            elif scope == "partial": self.show_indices.update((node.start_point[0], node.end_point[0]))
            if parents == "all":
                while node.parent:
                    self.show_indices.add(node.parent.start_point[0])
                    node = node.parent
        if last_line: self.show_indices.add(len(self.lines) - 1)
        return self
    
    def show_skeleton(self):
        self.show(query=f"{self.function_query()}\n{self.class_query()}", scope="line", parents="none")
        self.show(query=self.import_query(), scope="full", parents="none")
        return self
    
    def merge(self, other: "FileContext"):
        self.show_indices.update(other.show_indices)
        return self
    
    def add_comments(self, line_comment_map: Dict[int, str]):
        self.comments.update(line_comment_map)
        return self
    
    def walk_tree(self, node, depth=0):
        start = node.start_point
        end = node.end_point
        start_line = start[0]
        end_line = end[0]
        self.nodes[start_line].append(node)
        for i in range(start_line, end_line + 1):
            self.scopes[i].add(start_line)
        for child in node.children:
            self.walk_tree(child, depth + 1)
        return start_line, end_line
    
    def stringify(self, line_number=True, comment_prefix=""):
        if not self.show_indices: return ""
        small_gap_size = 2 # close small gaps
        closed_show = set(self.show_indices)
        sorted_show = sorted(self.show_indices)
        for i in range(len(sorted_show) - 1):
            if sorted_show[i + 1] - sorted_show[i] == small_gap_size:
                closed_show.add(sorted_show[i] + 1)
        self.show_indices = closed_show
        output = ""
        dots = not (0 in self.show_indices)
        for i, line in enumerate(self.code.splitlines()):
            if i not in self.show_indices:
                if dots:
                    if line_number: output += "...⋮...\n"
                    else: output += "⋮...\n"
                    dots = False
                continue
            spacer = "│"
            comment = self.comments.get(i + 1)
            if comment:
                comment_lines = [c.replace("#", "").replace("TODO:", "").strip() for c in comment.strip().splitlines()]
                border_spacing = " " * len(f"{i+1:3}")
                whitespace = line[:len(line) - len(line.lstrip())]
                for j, comment in enumerate(comment_lines):
                    output += f"{border_spacing}{spacer}{whitespace}#{comment_prefix if j == 0 else ""} {comment}\n"
            line_output = f"{spacer}{line}"
            if line_number: line_output = f"{i+1:3}" + line_output
            output += line_output + "\n"
            dots = True
        return output.rstrip()

if __name__ == "__main__":
    context = FileContext("hello.py")
    context.show(line_range=(15, 21), scope="line", parents="none")
    print(context.stringify(comment_prefix=" TODO(james|issue#123):"))