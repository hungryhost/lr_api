export const parseName = initialString => {
    const res = initialString.split(" ");
    return {
        first_name: res[0],
        last_name: res[1]
    }
}

console.log(parseName("Pavel Lapshin"))
console.log(parseName("Pavel"))
