from enum import Enum
import json


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

    def __init__(
        self, input_filename: str, input_format: Formats, output_format: Formats
    ):
        if output_format == input_format:
            raise ValueError("Input and output formats are the same")

        self.input_input_filename = input_filename
        self.output_filename = "result." + output_format.value
        self.input_format = input_format
        self.output_format = output_format

        self.data = self.open_file(input_filename, input_format)

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
                if xml[i + 1] == "/":
                    closing_tag = ""
                    i += 2
                    while xml[i] != ">":
                        closing_tag += xml[i]
                        i += 1
                    if closing_tag != tag_stack[-1][0]:
                        raise ValueError("Wrong xml format")
                    else:
                        if tag_stack[-1][1] > 1:
                            json_result += "}"
                        elif tag_stack[-1][1] == 1:
                            json_result = json_result[:-1] + "},"
                        else:
                            json_result += '"'
                        tag_stack.pop()

                else:
                    tag = ""
                    i += 1
                    while xml[i] != ">":
                        tag += xml[i]
                        i += 1
                    if tag_stack:
                        if tag_stack[-1][1] > 0:
                            json_result += ", "
                    json_result += '"' + tag + '":'
                    if tag_stack:
                        tag_stack[-1][1] += 1
                    tag_stack.append([tag, 0])
                    if xml[i + 1] != "<":
                        json_result += '"'
                    else:
                        json_result += "{"
            elif xml[i] == ">":
                if xml[i - 1] == "/":
                    tag_stack.pop()
                    json_result = json_result[:-1] + "},"
                else:
                    json_result += '"'
            else:
                if xml[i] != '"':
                    json_result += xml[i]
            i += 1

        json_result = json_result[:-1] + "}}"
        self.json_data = json_result
        self.write_file(self.output_filename, json_result, self.output_format)
        self.json_prettyfy()
        return json_result

    def json_prettyfy(self):
        with open(self.output_filename, "r") as file:
            d = json.load(file)
        with open(self.output_filename, "w") as file:
            json.dump(d, file, indent=4)

    @staticmethod
    def write_file(input_filename: str, data: str, output_format: Formats):
        with open(input_filename, "w") as file:
            if not input_filename.endswith(output_format.value):
                raise ValueError("Wrong file format")
            file.write(data)

    @staticmethod
    def open_file(input_filename: str, input_format: Formats):
        try:
            with open(input_filename, "r") as file:
                if not input_filename.endswith(input_format.value):
                    raise ValueError("Wrong file format")
                return file.read()
        except (FileNotFoundError, ValueError) as e:
            raise Parser.FileOpenError(message=str(e))


Parser("shedule.xml", Parser.Formats.XML, Parser.Formats.JSON).convert()
