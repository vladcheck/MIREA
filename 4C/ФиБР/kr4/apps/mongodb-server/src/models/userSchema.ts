import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
  age: { max: 120, min: 18, required: true, type: Number },
  created_at: { default: Date.now, required: true, type: Date },
  first_name: { required: true, type: String },
  last_name: { required: true, type: String },
  updated_at: { default: Date.now, required: true, type: Date },
});

export default userSchema;
