import type { Author, Book, Store } from "./types.js";

export const resolvers = ({
  books,
  authors,
  stores,
}: {
  books: Book[];
  authors: Author[];
  stores: Store[];
}) => {
  return {
    Query: {
      books: () => books,
      book: (_: unknown, { id }: Pick<Book, "id">) => books.find((b) => b.id === id) || null,

      stores: () => stores,
      store: (_: unknown, { id }: Pick<Store, "id">) => stores.find((b) => b.id === id) || null,

      authors: () => authors,
      author: (_: unknown, { id }: Pick<Author, "id">) => authors.find((b) => b.id === id) || null,
    },
    Mutation: {
      createAuthor: (_: unknown, { name }: Pick<Author, "name">) => {
        const newAuthor = {
          id: String(authors.length + 1),
          name,
        };

        authors.push(newAuthor);

        return newAuthor;
      },

      createBook: (_: unknown, { title, authorId }: Pick<Book, "title" | "authorId">) => {
        const newBook = {
          id: String(books.length + 1),
          title,
          authorId,
        };

        books.push(newBook);

        return newBook;
      },
    },
    Book: {
      author: (parent: Book) => {
        return authors.find((author) => author.id === parent.authorId);
      },
    },
    Author: {
      books: (parent: Author) => {
        return books.filter((book) => book.authorId === parent.id);
      },
    },
  };
};
