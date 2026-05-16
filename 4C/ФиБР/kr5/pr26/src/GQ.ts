export default class GQ {
  static Required = (type: string) => (type.endsWith("!") ? type : `${type}!`);
  static Collection = (type: string) =>
    type.startsWith("[") && type.endsWith("]") ? type : `[${type}]`;
  static Function = (name: string, returnType: string = "none", args: Record<string, string>) => {
    return {
      [`${name}(${Object.entries(args)
        .map(([k, t]) => `${k}: ${t}`)
        .join(", ")})`]: returnType,
    };
  };
}