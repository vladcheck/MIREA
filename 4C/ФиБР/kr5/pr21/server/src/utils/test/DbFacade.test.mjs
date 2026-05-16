import dbFacade from '../DbFacade.ts';

const dataMock = {
	id: '123456',
	title: 'Деревянная подставка для книги',
	price: 2000,
	score: 3.6,
	reviews: [],
};

const basename = 'users.json';

dbFacade
	.createFile('users.json')
	.then(() => dbFacade.appendEntry(basename, dataMock))
	.then(() => dbFacade.appendEntry(basename, dataMock))
	.then(() => dbFacade.readEntries(basename))
	.then((data) => console.log(data.length))
	.then(() => dbFacade.deleteAllEntries(basename))
	.then(() => dbFacade.deleteFile(basename))
	.catch((error) => console.error(error));
