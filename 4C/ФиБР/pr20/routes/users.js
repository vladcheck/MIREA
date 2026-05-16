const express = require('express')
const router = express.Router()
const User = require('../models/User')

router.post('/', async (req, res) => {
  try {
    const user = new User(req.body)
    await user.save()
    res.status(201).json(user)
  } catch (err) {
    res.status(400).json({ error: err.message })
  }
})

router.get('/', async (req, res) => {
  try {
    const users = await User.find()
    res.json(users)
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

router.get('/:id', async (req, res) => {
  try {
    const user = await User.findOne({ id: parseInt(req.params.id) })
    if (!user) return res.status(404).json({ error: 'User not found' })
    res.json(user)
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

router.patch('/:id', async (req, res) => {
  try {
    const user = await User.findOneAndUpdate(
      { id: parseInt(req.params.id) },
      req.body,
      { new: true }
    )
    if (!user) return res.status(404).json({ error: 'User not found' })
    res.json(user)
  } catch (err) {
    res.status(400).json({ error: err.message })
  }
})

router.delete('/:id', async (req, res) => {
  try {
    const user = await User.findOneAndDelete({ id: parseInt(req.params.id) })
    if (!user) return res.status(404).json({ error: 'User not found' })
    res.json({ message: 'User deleted', user })
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

module.exports = router