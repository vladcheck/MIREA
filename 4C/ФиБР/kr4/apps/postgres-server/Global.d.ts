export declare global {
  export type Config = Partial<
    Record<"POSTGRES_PASSWORD" | "POSTGRES_DB" | "POSTGRES_USER" | "POSTGRES_PORT" | "POSTGRES_HOST", string>
  >;
}
