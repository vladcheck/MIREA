const mongoose = require('mongoose')

const counterSchema = new mongoose.Schema({
  _id: { type: String, required: true },
  seq: { type: Number, default: 0 }
})
const Counter = mongoose.model('Counter', counterSchema)

const userSchema = new mongoose.Schema({
  id: { type: Number, unique: true },
  first_name: { type: String, required: true },
  last_name: { type: String, required: true },
  age: { type: Number, required: true },
  created_at: { type: Number, default: () => Math.floor(Date.now() / 1000) },
  updated_at: { type: Number }
}, { timestamps: false })

userSchema.pre('save', async function (next) {
  if (this.isNew) {
    const counter = await Counter.findOneAndUpdate(
      { _id: 'userId' },
      { $inc: { seq: 1 } },
      { new: true, upsert: true }
    )
    this.id = counter.seq
  }
  this.updated_at = Math.floor(Date.now() / 1000)
  next()
})

module.exports = mongoose.model('User', userSchema)