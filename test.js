// お題1：数値ジャッジ（符号✕偶奇）

n = 10

if (n % 2 === 0) {
  if (n > 0) {
    console.log("positive even");
  } else if (n === 0) {
    console.log("zero even");
  } else {
    console.log("negative even")
  };
} else {
  if (n > 0) {
    console.log("positive odd");
  } else {
    console.log("negative odd")
  };
};