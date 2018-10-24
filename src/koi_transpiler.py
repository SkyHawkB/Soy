import pathlib

from .gen.KoiParser import KoiParser
from .gen.KoiListener import KoiListener


class KoiTranspiler(KoiListener):
    def __init__(self):
        pathlib.Path("out").mkdir(exist_ok=True)
        # TODO: Change to use the Koi file name
        # TODO: Create an associating header
        self.file = open("out/main.c", "w")

        self.current_line = ["#include <stdio.h>\n"]
        self.current_name = ""
        self.secondary_name = ""

        self.loop_name = "index"

    def exitLine(self, ctx:KoiParser.LineContext):
        self.file.write(" ".join(self.current_line))
        self.current_line = []

    def enterBlock(self, ctx:KoiParser.BlockContext):
        self.current_line.append("{")

        if type(ctx.parentCtx) is KoiParser.For_blockContext:
            self.current_line.append(self.secondary_name)
            self.current_line.append("=")
            self.current_line.append(self.current_name)
            self.current_line.append("[")
            self.current_line.append(self.loop_name)
            self.current_line.append("]")
            self.current_line.append(";")

    def exitBlock(self, ctx:KoiParser.BlockContext):
        self.current_line.append("}")

    def enterFunction_block(self, ctx:KoiParser.Function_blockContext):
        self.current_line.append(ctx.returnType.getText())
        self.current_line.append(ctx.name().getText())

    def enterParameter_set(self, ctx:KoiParser.Parameter_setContext):
        self.current_line.append("(")

    def exitParameter_set(self, ctx:KoiParser.Parameter_setContext):
        self.current_line.append(")")

    def enterName(self, ctx:KoiParser.NameContext):
        self.current_name = ctx.getText()

    def enterType_(self, ctx:KoiParser.Type_Context):
        if type(ctx.parentCtx) is not KoiParser.Type_Context and type(ctx.parentCtx) is not KoiParser.Function_blockContext:
            if ctx.getText().startswith("str"):
                self.current_line.append("char*")

            else:
                self.current_line.append(ctx.getText().split("[]")[0])

        if type(ctx.parentCtx) is KoiParser.ParameterContext:
            self.current_line.append(self.current_name + ("[]" if "[]" in ctx.getText() else ""))

            params = []

            for i in ctx.parentCtx.parentCtx.parameter():
                params.append(i.name().getText())

            if len(params) > 0:
                if params.index(self.current_name) < len(params) - 1:
                    self.current_line.append(",")

            self.current_name = ""

    def enterReturn_stmt(self, ctx:KoiParser.Return_stmtContext):
        self.current_line.append("return")
        self.current_line.append(ctx.true_value().getText())
        self.current_line.append(";")

    def enterFunction_call(self, ctx:KoiParser.Function_callContext):
        # TODO: Write the console library and add imports
        if ctx.funcName.getText() in ["print", "println"]:
            self.current_line.append("printf")

        else:
            self.current_line.append(ctx.funcName.getText())

        self.current_line.append("(")

        # TODO: Resolve the order of parameters
        for v in ctx.paramValues:
            self.current_line.append(v.getText())

            if len(ctx.paramValues) > 0:
                if ctx.paramValues.index(v) < len(ctx.paramValues) - 1:
                    self.current_line.append(",")

        self.current_line.append(")")
        self.current_line.append(";")

        if ctx.funcName.getText() == "println":
            self.current_line.append("printf")
            self.current_line.append("(")
            self.current_line.append("\"\\n\"")
            self.current_line.append(")")
            self.current_line.append(";")

    def enterFor_block(self, ctx:KoiParser.For_blockContext):
        self.current_name = ctx.name()[0].getText()
        self.current_line.append("int")
        self.current_line.append(self.loop_name)
        self.current_line.append(";")

        # FIXME: Use the array's type instead
        self.current_line.append("char*")
        self.current_line.append(self.current_name)
        self.current_line.append(";")

        self.current_line.append("for")
        self.current_line.append("(")
        self.current_line.append(self.loop_name)
        self.current_line.append("=")
        self.current_line.append("0")

        self.current_line.append(";")

        self.current_line.append(self.loop_name)
        self.current_line.append("<")
        self.current_line.append("sizeof")
        self.current_line.append("(")

        if ctx.with_length() is None:
            self.current_line.append(ctx.name()[1].getText())

        else:
            self.current_line.append(ctx.with_length().getText())

        self.secondary_name = ctx.name()[0].getText()

        self.current_line.append(")")
        self.current_line.append(";")
        self.current_line.append(self.loop_name)
        self.current_line.append("++")
        self.current_line.append(")")

