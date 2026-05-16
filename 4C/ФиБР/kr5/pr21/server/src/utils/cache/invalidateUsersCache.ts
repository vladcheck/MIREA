import buildInvalidator from "./lib/buildInvalidator";

const invalidateUsersCache = buildInvalidator("users:all");
export default invalidateUsersCache;
