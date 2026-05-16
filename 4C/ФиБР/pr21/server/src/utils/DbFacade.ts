import fs from "node:fs/promises";
import jsonfile from "jsonfile";

type DbEntry = { id: string };

class DbFacade {
  async readEntries<T extends DbEntry>(path: string): Promise<T[]> {
    const data: T[] = await jsonfile.readFile(path, { encoding: "utf8" });
    return data;
  }

  async appendEntry<T extends DbEntry>(path: string, entry: T): Promise<void> {
    const data: T[] = await this.readEntries(path);
    await jsonfile.writeFile(path, [...data, entry], { flag: "w", spaces: 2 });
    console.log(`Appended new entry to '${path}'`);
  }

  async updateEntryById<T extends DbEntry>(path: string, id: string, entry: T): Promise<void> {
    const data: T[] = await this.readEntries(path);
    const updatedData = data.map((e) => (e.id === id ? entry : e));
    await jsonfile.writeFile(path, updatedData, { flag: "w", spaces: 2 });
    console.log(`Updated entry '${id}' in '${path}'`);
  }

  async deleteEntryById<T extends DbEntry>(path: string, id: string): Promise<void> {
    const data: T[] = await this.readEntries(path);
    const updatedData = data.filter((entry) => entry.id !== id);
    await jsonfile.writeFile(path, updatedData, { flag: "w", spaces: 2 });
    console.log(`Deleted entry '${id}' from '${path}'`);
  }

  async createFile<T extends DbEntry>(path: string, entries?: T[]): Promise<boolean> {
    try {
      await fs.access(path, fs.constants.R_OK);
      return false;
    } catch {
      await fs.writeFile(path, "[]");

      if (entries) {
        for (const entry of entries) {
          await this.appendEntry(path, entry);
        }
      }
      console.log("File created successfully");
      return true;
    }
  }

  async deleteAllEntries(path: string): Promise<void> {
    await jsonfile.writeFile(path, [], { flag: "w", spaces: 2 });
    console.log(`All entries deleted from '${path}'`);
  }

  async deleteFile(path: string): Promise<void> {
    await fs.rm(path);
    console.log(`File '${path}' deleted`);
  }
}

const dbFacade = new DbFacade();
export default dbFacade;
