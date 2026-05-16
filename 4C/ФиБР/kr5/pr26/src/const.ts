import type { Book, Author, Store } from "./types.js";

export const defaultAuthors: Author[] = [
  {
    id: "1",
    name: "Stiven King",
    born: 1947,
  },
  {
    id: "2",
    name: "Raf Malik",
    born: 1948,
  },
  {
    id: "3",
    name: "R.W. Chembers",
    born: 1865,
  },
  {
    id: "4",
    name: "Miley Cyrus",
    born: 1992,
  },
];

export const defaultBooks: Book[] = [
  {
    id: "1",
    title: "King in Yellow",
    authorId: "3",
  },
  {
    id: "2",
    title: "Samsara Law",
    authorId: "2",
  },
  {
    id: "3",
    title: "It",
    authorId: "1",
  },
  {
    id: "4",
    title: "How I became a cowboy",
    authorId: "4",
  },
];

export const defaultStores: Store[] = [
  {
    id: "1",
    bookId: "1",
  },
  {
    id: "1",
    bookId: "2",
  },
];
