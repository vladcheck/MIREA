"""mirea-mcp: MCP-сервер для данных РТУ МИРЭА (СДО + Пульс).

Источники (ADR-0002): СДО — канон текущих данных (дисциплины, задания, баллы);
Пульс — посещаемость, расписание, группы. ЛКС вне scope.
"""
from fastmcp import FastMCP

from .tools import auth_tools, plan_tools, pulse_tools, sdo_tools, submit_tools

mcp = FastMCP("mirea-mcp")

for _mod in (auth_tools, sdo_tools, pulse_tools, plan_tools, submit_tools):
    _mod.register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
