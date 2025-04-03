from common.processor.processor import Processor as p
class Benchmark(object):

    @staticmethod
    def convert_to_benchmark(df,benchmark_column):
        df = p.lower_column(df)
        df = p.utc_date(df).sort_values("date")
        df.rename(columns={benchmark_column: "benchmark"}, inplace=True)
        df = df[["date","benchmark"]].dropna()
        return df   