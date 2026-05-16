import { ApolloServer } from "@apollo/server";
import { startStandaloneServer } from "@apollo/server/standalone";
import GQ from "./GQ.ts";
import GraphQLQuery from "./GraphQLQuery.ts";
import { defaultAuthors, defaultBooks, defaultStores } from "./const.ts";
import { resolvers } from "./resolvers.ts";

async function main() {
  const query = new GraphQLQuery()
    .defineType("Author", {
      id: GQ.Required("ID"),
      name: GQ.Required("String"),
      books: GQ.Collection("Book"),
      born: "Int",
    })
    .defineType("Book", {
      id: GQ.Required("ID"),
      title: GQ.Required("String"),
      author: "Author",
    })
    .defineType("Store", {
      id: GQ.Required("ID"),
      books: GQ.Collection("Book"),
    })
    .defineType("Query", {
      books: GQ.Collection("Book"),
      stores: GQ.Collection("Store"),
      authors: GQ.Collection("Author"),
      ...GQ.Function("book", "Book", { id: GQ.Required("ID") }),
      ...GQ.Function("store", "Store", { id: GQ.Required("ID") }),
      ...GQ.Function("author", "Author", { id: GQ.Required("ID") }),
    })
    .defineType("Mutation", {
      ...GQ.Function(`createAuthor`, "Author", { name: GQ.Required("String") }),
      ...GQ.Function(`createBook`, "Book", {
        title: GQ.Required("String"),
        authorId: GQ.Required("ID"),
      }),
    });

  const server = new ApolloServer({
    typeDefs: query.query,
    resolvers: resolvers.call(null, {
      books: defaultBooks,
      authors: defaultAuthors,
      stores: defaultStores,
    }),
  });

  const { url } = await startStandaloneServer(server, {
    listen: { port: 4000 },
  });

  console.log(`Type definitions:\n${query.color()}\n`);
  console.log(`Server ready at ${url}`);
  console.log(`sandbox: https://studio.apollographql.com/sandbox`)
}

main();
