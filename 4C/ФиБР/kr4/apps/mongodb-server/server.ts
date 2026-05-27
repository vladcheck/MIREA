import "dotenv/config";
import { StatusCodes } from "http-status-codes";
import { asyncHandler } from "./src/utils/asyncHandler.ts";
import express from "express";
import mongoose from "mongoose";
import userSchema from "./src/models/userSchema.ts";

const SERVER_ID = process.env.SERVER_ID || "mongo-unknown";
const PORT = parseInt(process.env.PORT || "3000");
const MONGODB_URI =
  process.env.MONGODB_URI || "mongodb://localhost:27017/admin";

const app = express();

mongoose
  .connect(MONGODB_URI)
  .then(() => console.log(`[${SERVER_ID}] Connected to MongoDB`))
  .catch((err) => console.error("Connection error:", err));

const User = mongoose.model("User", userSchema);

app.use(express.json());

// Add server ID to all responses
app.use((req, res, next) => {
  const originalSend = res.send.bind(res);
  res.send = (body) => {
    if (typeof body === "object" && body !== null && !Array.isArray(body)) {
      return originalSend({ ...body, _server_id: SERVER_ID });
    }
    return originalSend(body);
  };
  next();
});

app.get("/", (_, res) => {
  res.status(StatusCodes.OK).send({ status: "OK", server: SERVER_ID });
});

app.get("/api", (_, res) => {
  res.status(StatusCodes.OK).send({ status: "OK", server: SERVER_ID });
});

app.get(
  "/api/users",
  asyncHandler(async (_, res) => {
    const users = await User.find();
    res.send(users);
  }),
);

app.post(
  "/api/users",
  asyncHandler(async (req, res) => {
    const user = new User(req.body);
    await user.save();
    res.status(StatusCodes.CREATED).send(user);
  }),
);

app.get(
  "/api/users/:id",
  asyncHandler(async (req, res) => {
    const user = await User.findById(req.params.id);
    res.send(user);
  }),
);

app.patch(
  "/api/users/:id",
  asyncHandler(async (req, res) => {
    const user = await User.findByIdAndUpdate(req.params.id, req.body, {
      returnDocument: "after",
      runValidators: true,
    });
    if (!user) {
      return res.status(StatusCodes.NOT_FOUND).send("User not found");
    }
    res.send(user);
  }),
);

app.delete(
  "/api/users/:id",
  asyncHandler(async (req, res) => {
    const user = await User.findByIdAndDelete(req.params.id);
    if (!user) {
      return res.status(StatusCodes.NOT_FOUND).send("User not found");
    }
    res.send(user);
  }),
);

app.use(
  (
    err: Error,
    _req: express.Request,
    res: express.Response,
    _next: express.NextFunction,
  ) => {
    console.error("Unhandled error:", err);
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).send(err.message);
  },
);

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server ${SERVER_ID} running on http://0.0.0.0:${PORT}`);
});
