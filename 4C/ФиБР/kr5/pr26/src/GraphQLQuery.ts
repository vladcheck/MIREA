import PaintedString from "./shared/PaintedString.ts";

export default class GraphQLQuery {
  private _query: `#graphql${string}` = "#graphql";

  defineType(name: string, pairs: Record<string, string>) {
    this._query += `
    type ${this.normalizeName(name)} {
      ${Object.entries(pairs)
        .map(([k, v]) => `\t${k}: ${v},`)
        .join("\n")}
    }`;
    return this;
  }

  private normalizeName(dirtyName: string) {
    const name = dirtyName.trim().toWellFormed();
    return name[0]?.toLocaleUpperCase() + name.slice(1).toLocaleLowerCase();
  }

  public color(): string {
    return new PaintedString(this.query)
      .green("#graphql")
      .brightBlue("type")
      .brightBlue("{")
      .brightBlue("}")
      .red("!").out;
  }

  get query() {
    return this._query;
  }
}
