/** Deterministic scenario model. No financial assumptions are supplied by the code. */
export function project({price, variableCost, monthlyCapacity, years}) {
  const nonnegative = n => typeof n === 'number' && Number.isFinite(n) && n >= 0 && n <= 1e12;
  if (!nonnegative(price) || price === 0 || !nonnegative(variableCost) ||
      !Number.isInteger(monthlyCapacity) || monthlyCapacity < 1 || monthlyCapacity > 10000 ||
      !Array.isArray(years) || years.length !== 3) throw new RangeError('invalid-input');
  const contribution = price - variableCost;
  const annualCapacity = monthlyCapacity * 12;
  const rows = years.map(({units, fixedCosts},index) => {
    if (!Number.isInteger(units) || units < 0 || units > annualCapacity || !nonnegative(fixedCosts))
      throw new RangeError('invalid-input');
    const revenue = units * price;
    const variableCosts = units * variableCost;
    const totalCosts = variableCosts + fixedCosts;
    const result = revenue - totalCosts;
    return {year:index + 1, units, revenue, variableCosts, fixedCosts, totalCosts, result,
      margin: revenue === 0 ? null : result/revenue*100,
      breakEven: contribution > 0 ? Math.ceil(fixedCosts/contribution) : null,
      utilisation: units/annualCapacity*100};
  });
  return {rows,contribution,annualCapacity,totalResult:rows.reduce((sum,r)=>sum+r.result,0)};
}
