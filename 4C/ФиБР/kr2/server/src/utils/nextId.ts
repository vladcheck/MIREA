import { nanoid } from 'nanoid';

const ID_SIZE = 32;
export default (id = ID_SIZE) => nanoid(id);
