const songName = "I'm a barbie girl 🎶";
console.log(`Now playing ${songName}`);

const catMood = "angry 😾";
console.log(`Your cat is ${catMood}`);

const isImpostor = true;
console.log(`Red is impostor? ${isImpostor}`);

const wow = "wow";
const soJS = "so JavaScript";
const muchCode = "much code";
console.log(wow, soJS, muchCode);

const likes = 77;
const verified = false;
console.log(typeof likes, typeof verified);

const isOnion = true;
console.log(typeof isOnion);

const year = 2077;
const hero = "V";
const isBuggy = true;
console.log(typeof year, typeof hero, typeof isBuggy);

const prize = 1000000;
console.log(typeof prize);

const nickname = prompt("What’s your Minecraft nickname?");
alert(`Welcome to the server, ${nickname} ⛏️`);

const favorite = prompt("What’s your favorite TV show?");
alert(`Tonight we binge: ${favorite} 🍿`);

const coolDocs = confirm("Do you want a link to cool JS docs");
if (coolDocs.toString().toLocaleLowerCase() == "ok") {
  alert("Never gonna give you up 🎵");
}

const hoursScroll = confirm("How many hours did you scroll today?");
alert(`Bruh, that's ${hoursScroll} hours... touch grass 🌱`);

const bitcoin = parseInt(prompt("Bitcoin?"));
console.log(`Skibidi `.repeat(bitcoin));

const coffees = +prompt("How many coffees today?") + 1;
console.log(coffees);

const karma = +prompt("Karma?");
console.log("Total karma: " + (karma + 10));

const postLikes = +prompt("How many likes did your post get?");
console.log(postLikes + 420);

const money = 1000;
console.log(money + 250);

const coins = 350;
const boosters = 5;
console.log("Total score: " + (coins + boosters * 100));

const pikachuHP = 100,
  attack = 35;
console.log(pikachuHP - attack);

const players = 456,
  eliminated = 100;
console.log(players - eliminated);

const a = 10,
  b = 3;
console.log(a / b, a % b);
