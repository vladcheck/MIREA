import buildInvalidator from "./lib/buildInvalidator";

const invalidateProductCache = buildInvalidator("products:all");
export default invalidateProductCache;
