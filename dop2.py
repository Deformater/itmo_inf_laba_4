from enum import Enum
import json
import re


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
        self.output_filename = "result2." + output_format.value
        self.input_format = input_format
        self.output_format = output_format

        self.data = self.open_file(input_filename, input_format)

    def __input_data_serializer(self):
        data_lines = "".join(list(map(lambda x: x.strip(), self.data.split("\n")[1:])))
        return data_lines

    def convert(self):
        xml = self.__input_data_serializer()
        json_result = {}
        tag_stack = []
        i = 0
        
        r = re.compile(r"<[^>/]*>[^<>]+</[^>]*>")
        values = r.findall(xml)
        
        r1 = re.compile(r">([^>]*)<")
        r2 = re.compile(r"<([^>]*)>")
        tag_values_arr = list(map(lambda x: [r2.findall(x)[0], r1.findall(x)[0]], values))
        arr = [tag_values_arr[0][1]]
        res = []
        # for i in range(1, len(tag_values_arr)):
        #     k, v = tag_values_arr[i]
        #     kl, vl = tag_values_arr[i - 1]
        #     if k == kl:
        #         arr.append(v)
        #     else:
        #         res.append((kl, arr))
        #         arr = [v]
        # res.append((k, arr))
        res = tag_values_arr[:]
        
        s = '{'
        tags = r2.findall(xml)
        for i in range(len(tags)):
            if tags[i][0] != "/":
                if tag_stack:
                    if tag_stack[-1][1] > 0:
                        s += ','
                    tag_stack[-1][1] += 1
                tag_stack.append([tags[i], 0])
                s += '"' + tags[i] +'"' + ':'
                if tag_stack[-1][0] not in list(map(lambda x: x[0], res)):
                    s += '{'
            else:
                if tag_stack[-1][0] == tags[i][1:]:
                    if tag_stack[-1][0] in list(map(lambda x: x[0], res)):
                        k = list(map(lambda x: x[0], res)).index(tag_stack[-1][0])
                        res[k][1] = res[k][1].replace('"', '')
                        s += '"' + res[k][1] + '"'
                        res.pop(k)
                    else:
                        s += '}'
                    tag_stack.pop(-1)
        s += '}'
                    
        self.json_data = json_result
        self.write_file(self.output_filename, s, self.output_format)
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
