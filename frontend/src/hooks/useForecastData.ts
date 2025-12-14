import { useMemo } from 'react'

export function useForecastData(result: any) {
  return useMemo(() => {
    if (!result || !result.series) return []
    return result.series.map((r: any) => ({ date: r.date, forecast: r.forecast }))
  }, [result])
}
