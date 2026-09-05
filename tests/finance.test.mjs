import {test} from 'node:test';
import assert from 'node:assert/strict';
import {project} from '../app/static/js/finance-model.mjs';
// Synthetic fixtures for arithmetic verification, not company forecasts.
const fixture={price:100,variableCost:60,monthlyCapacity:2,years:[{units:10,fixedCosts:500},{units:20,fixedCosts:500},{units:24,fixedCosts:600}]};
test('reconciles revenue, variable costs, fixed costs and signed result',()=>{
 const p=project(fixture);assert.deepEqual(p.rows.map(r=>r.result),[-100,300,360]);
 assert.equal(p.totalResult,560);assert.equal(p.rows[0].breakEven,13);assert.equal(p.rows[0].margin,-10);
 for(const r of p.rows)assert.equal(r.revenue-r.variableCosts-r.fixedCosts,r.result);
});
test('handles no sales without invented margin',()=>{
 const p=project({...fixture,years:Array.from({length:3},()=>({units:0,fixedCosts:500}))});
 assert.equal(p.rows[0].result,-500);assert.equal(p.rows[0].margin,null);
});
test('rejects output beyond declared capacity and invalid numbers',()=>{
 assert.throws(()=>project({...fixture,years:[{units:25,fixedCosts:500},...fixture.years.slice(1)]}),RangeError);
 for(const price of [null,NaN,Infinity,-1,0,'100'])assert.throws(()=>project({...fixture,price}),RangeError);
});
test('does not claim a break-even volume with nonpositive contribution',()=>{
 assert.equal(project({...fixture,variableCost:100}).rows[0].breakEven,null);
 assert.equal(project({...fixture,variableCost:110}).rows[0].breakEven,null);
});
