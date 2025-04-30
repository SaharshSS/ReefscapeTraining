const base_path = '/World/Cams_01/';

function cam_name(num){
    return num === 0 ? base_path+"Camera" : base_path+`Camera_${String(num).padStart(2, "0")}`;
}

function cam(name, size){
    return `[
    "${name}",
    ${size},
    ${size},
    ""
]`;
}

const arr = [];
for(let i = 0; i < 50; i++) arr.push(cam_name(i));
const str = arr.map(name => cam(name, 512)).join(', \n');
console.log(str);