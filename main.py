from enum import Enum


class Parser:
    class FileOpenError(Exception):
        def __init__(self, message: str) -> None:
            self.message = message

        def __str__(self) -> str:
            return f"File open error: {self.message}"

    class Formats(Enum):
        XML = "xml"
        JSON = "json"
        YAML = "yaml"

    def __init__(self, filename: str, input_format: Formats, output_format: Formats):
        if output_format == input_format:
            raise ValueError("Input and output formats are the same")

        self.filename = filename
        self.input_format = input_format
        self.output_format = output_format

        self.data = self.open_file(filename, input_format)

    def __input_data_serializer(self):
        data_lines = "".join(list(map(lambda x: x.strip(), self.data.split("\n")[1:])))
        return data_lines

    def convert(self):
        xml = self.__input_data_serializer()
        json_result = "{"
        tag_stack = []
        i = 0

        while i < len(xml):
            if xml[i] == "<":
                if xml[i+1] == "/":
                    closing_tag = ""
                    i += 2
                    while xml[i] != ">":
                        closing_tag += xml[i]
                        i += 1
                    if tag_stack and tag_stack[-1] == closing_tag:
                        tag_stack.pop()
                        json_result += "}"
                        if i + 1 < len(xml) and xml[i+1] != "<":
                            json_result += ","
                    else:
                        raise ValueError("Mismatched tags in XML")
                else:
                    tag = ""
                    i += 1
                    while xml[i] != ">":
                        tag += xml[i]
                        i += 1
                    if tag_stack:
                        json_result += ','
                    json_result += '"' + tag + '":'
                    tag_stack.append(tag)
                    if xml[i+1] != "<":
                        json_result += '"'
                    else:
                        json_result += "{"
            elif xml[i] == ">":
                if xml[i-1] == "/":
                    tag_stack.pop()
                    json_result = json_result[:-1] + "},"
                else:
                    json_result += '"'
            else:
                if xml[i] != "\n" and xml[i] != "\t":
                    json_result += xml[i]
            i += 1

        json_result = json_result[:-1] + "}"
        return json_result


    @staticmethod
    def open_file(filename: str, input_format: Formats):
        try:
            with open(filename, "r") as file:
                if not filename.endswith(input_format.value):
                    raise ValueError("Wrong file format")
                return file.read()
        except (FileNotFoundError, ValueError) as e:
            raise Parser.FileOpenError(message=str(e))


print(Parser("shedule.xml", Parser.Formats.XML, Parser.Formats.JSON).convert())
