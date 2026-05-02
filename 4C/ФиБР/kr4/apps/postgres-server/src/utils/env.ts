export function getEnvVarSafely(name: string): string {
  if (!process.env[name]) {
    throw new Error(`process.env.${name} is not set`);
  }
  return process.env[name];
}
