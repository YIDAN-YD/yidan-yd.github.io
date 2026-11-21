import http from 'node:http';
const {default:worker}=await import('../worker/local-bundle.mjs');
const port=Number(process.env.ATLAS_PREVIEW_PORT||8765);
const server=http.createServer(async(req,res)=>{try{const response=await worker.fetch(new Request('http://localhost:'+port+req.url,{method:req.method,headers:req.headers}),{}, {waitUntil:p=>p.catch(()=>{})});res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));}catch(e){res.writeHead(500);res.end('Preview error');console.error(e.message);}});server.listen(port,'127.0.0.1',()=>console.log('Local: http://localhost:'+port));
