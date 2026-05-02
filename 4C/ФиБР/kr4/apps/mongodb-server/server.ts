import 'dotenv-defaults/config';
import { StatusCodes } from "http-status-codes"
import express from 'express';
import mongoose from 'mongoose';
import userSchema from './models/userSchema.ts';

const app = express();

const config = {
  admin: "admin",
  port: 27017,
}

mongoose.connect(`mongodb://${config.admin}:1234@localhost:${config.port}/admin`)
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('Connection error:', err));
const User = mongoose.model('User', userSchema);

app.use(express.json());

app.get('/api/users', async (req, res) => {
  try {
    const users = await User.find();
    res.send(users);
  } catch (err: any) {
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).send(err.message);
  }
});

app.get('/api/users/:id', async (req, res) => {
  try {
    const users = await User.findById({ id: req.body.id });
    res.send(users);
  } catch (err: any) {
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).send(err.message);
  }
});

app.post('/api/users', async (req, res) => {
  try {
    const user = new User(req.body);
    await user.save();
    res.status(StatusCodes.CREATED).send(user);
  } catch (err: any) {
    res.status(StatusCodes.BAD_REQUEST).send(err.message);
  }
});

app.patch('/api/users/:id', async (req, res) => {
  try {
    const user = await User.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true } // Возвращает обновленный документ
    );
    if (!user) { return res.status(StatusCodes.NOT_FOUND).send('User not found'); }
    res.send(user);
  } catch (err: any) {
    res.status(StatusCodes.BAD_REQUEST).send(err.message);
  }
});

app.delete('/api/users/:id', async (req, res) => {
  try {
    const user = await User.findByIdAndDelete(req.params.id);
    if (!user) { return res.status(StatusCodes.NOT_FOUND).send('User not found'); }
    res.send(user);
  } catch (err: any) {
    res.status(StatusCodes.INTERNAL_SERVER_ERROR).send(err.message);
  }
});

app.listen(process.env.PORT, () => {
  console.log('Server is running on http://localhost:3000');
});