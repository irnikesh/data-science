import argparse

from client import ClientS3

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download single file from S3")
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--prefix", type=str, default="file.csv", required=True)
    parser.add_argument("--bucket", type=str, default="bucket", required=False)
    args = parser.parse_args()

    client = ClientS3()
    lst_df = client.download_csvs(args.bucket, args.prefix)

    print("Csvs downloaded: {}".format(len(lst_df)))

    # NOTE: dump to disk only first df from the list. Ideally - it must be exactly one df in the result.
    if len(lst_df) > 0:
        lst_df[0].to_csv(args.output)
