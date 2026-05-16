import { ApolloServer } from "@apollo/server"
import { startStandaloneServer } from "@apollo/server/standalone"

const authors = [
  {
    id: '1',
    name: 'Stiven King'
  },
  {
    id: '2',
    name: 'RafMilk'
  },
  {
    id: '3',
    name: 'Chembers'
  },
  {
    id: '4',
    name: 'Frrk'
  }
]

const books = [
  {
    id: '1',
    title: 'King in Yellow',
    authorId: '3'
  },
  {
    id: '2',
    title: 'Samsara Law',
    authorId: '2'
  },
  {
    id: '3',
    title: 'It',
    authorId: '1'
  },
  {
    id: '4',
    title: 'Saaaas',
    authorId: '4'
  }
]

const typeDefs = `#graphql
    type Author {
        id: ID!
        name: String!
        books: [Book]
    }

    type Book {
        id: ID!
        title: String!
        author: Author
    }

    type Query {
        books: [Book]
        book(id: ID!): Book
        authors: [Author]
    }

    type Mutation {
        createAuthor(name: String!): Author
        createBook(title: String!, authorId: ID!): Book
    }
`

const resolvers = {
  Query: {
    books: () => books,

    book: (_, { id }) => {
      const book = books.find(b => b.id === id)
      return book || null
    },

    authors: () => authors
  },
  Mutation: {
    createAuthor: (_, { name }) => {
      const newAuthor = {
        id: String(authors.length + 1),
        name
      }

      authors.push(newAuthor)

      return newAuthor
    },

    createBook: (_, { title, authorId }) => {
      const newBook = {
        id: String(books.length + 1),
        title,
        authorId
      }

      books.push(newBook)

      return newBook
    }
  },
  Book: {
    author: (parent) => {
      return authors.find(author => author.id === parent.authorId)
    }
  },
  Author: {
    books: (parent) => {
      return books.filter(book => book.authorId === parent.id)
    }
  }
}

const server = new ApolloServer({
  typeDefs,
  resolvers
})

const { url } = await startStandaloneServer(server, {
  listen: { port: 4000 }
})

console.log(`Server ready at ${url}`)