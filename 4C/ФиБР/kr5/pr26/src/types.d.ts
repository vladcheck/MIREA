export interface Author {
  id: string;
  name: string;
  born?: number;
}

export interface Book {
  id: string;
  title: string;
  authorId: string;
}

export interface Store {
  id: string;
  bookId: string;
}
