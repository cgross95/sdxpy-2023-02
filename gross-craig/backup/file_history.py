import argparse
from manifest_utils import (read_manifest, join_manifests, find_hash,
                            get_manifest_paths, RESULT_TEMPLATE)


def parse_changes(filename, comparison, manifests):
    """Report the changes in a file over a comparison of manifests

    Parameters
    ----------
    filename : Name of file to report changes
    comparison : Dictionary of hashes over all manifests
        (see manifest_utils.join_manfests for more information)
    manifests : Paths of all manifests in same order as values in comparison

    Returns
    -------
    A dictionary with manifests as keys and tuples of status and filename as
    values

    """
    hashes = comparison.get(filename, [])
    report = {}
    for i, (new_hash, manifest_path) in enumerate(zip(hashes, manifests)):
        old_hash = None if i == 0 else hashes[i - 1]
        manifest = manifest_path.stem
        if old_hash is None:
            if new_hash is not None:
                report[manifest] = ("added", filename)
                pass
        else:  # old_hash is not None
            if new_hash is None:
                matches = find_hash(comparison, old_hash, col=i)
                if matches:
                    report[manifest] = ("renamed", [filename, matches[0]])
                    pass
                else:
                    report[manifest] = ("deleted", filename)
                    pass
                pass
            elif new_hash != old_hash:
                report[manifest] = ("changed", filename)
                pass
    return report


def print_change_report(file, report):
    """Print the changes of a file over all manifests

    Parameters
    ----------
    file : The filename to print the history of
    report : A report produced by parse_changes

    Returns
    -------
    None

    """
    print_string = []
    if len(report.items()) == 0:
        print_string.append(f"File {file} not found")
    for manifest, (status, file) in sorted(report.items()):
        print_string.append(f"{RESULT_TEMPLATE[status](file)} in {manifest}")
    print("\n".join(print_string))


def main(file, manifest_dir):
    """TODO:

    Parameters
    ----------
    file : Name of file to produce history for
    manifest_dir : The directory to search for manifest files

    Returns
    -------
    A report of all changes as generated by parse_changes

    """
    # Get all manifest names
    manifest_paths = get_manifest_paths(manifest_dir)
    # Load all manifests
    manifests = [read_manifest(path) for path in manifest_paths]
    comparison = join_manifests(*manifests)
    # Read through filename line and report changes
    report = parse_changes(file, comparison, manifest_paths)
    print_change_report(file, report)
    return report


if __name__ == "__main__":
    USAGE = "Displays history of file by tracing it through all manifests"
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument("file", type=str, help="Input file name")
    parser.add_argument("-d", "--manifest_dir", type=str, default=".",
                        help="Directory containing manifests")
    args = parser.parse_args()
    main(args.file, args.manifest_dir)
