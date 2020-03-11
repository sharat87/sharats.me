---
title: The `tar` Command Clipboard
tags: [shell, bash, tar, tutorial, command-clipboard]
description: >
    The tar command clipboard, quick reference for common needs with the `tar` command.
---

Recently, while doing an experiment with my blog's rendered output with a VPS instance, I needed to
transfer it to the server over SSH. While doing that, I experimented with archiving the folder a
bit, so I'm putting the outcome of that experience here, should I need it again in the future.

All notes below assume GNU `tar v1.26`. More specifically, the output of `tar --version | head -1`
gives:

    tar (GNU tar) 1.26

I'm only listing the arguments and use-cases that I think are most frequently used (at least by me)
and the ones I'm most likely to need in the future. Please complement this with a healthy serving of
`man tar` to keep your sanity.

Check out this neat little tool to help generate often-used `tar` commands:
[cligen.sharats.me](https://cligen.sharats.me). Thanks!
{: .note }

[TOC]

## Creating Archives

The `-c` (or `--create`) command is used to **create** archives.

The `-` in front of the `c` can be omitted, but I find that ugly and prefer to include it. That way
it's consistent with most other such GNU commands.
{: .note }

Additional options after `-c`:

1. `v` -- Enable verbose output. Adding this will print each file as it is being added to the
   archive.

1. `z` or `j` -- Specify the compression format, if needed. Use `z` for `gz` archive or `j` for
   `bz2` archive. This can also be `a` to infer the compression format from the file name, but only
   if the `f` (explained in the next point) is also given. Other compression formats like `--xz`,
   `--lzip` etc. can also be used.

1. `f` -- Use the next argument as the file name of the archive. If this argument is not provided,
   the archive content is written to the standard out.

1. `--remove-files` -- Remove files after adding them to the archive. Be careful with this.

To illustrate the examples, I'll clone one of my public repositories and play around with creating
archives of it.

```console
$ git clone git@github.com:sharat87/just-a-calendar.git
$ du -sh just-a-calendar
248K    just-a-calendar/
```

### Create a `.tar.bz2` Archive

To create a `bz2` archive of a folder:

```console
$ tar -cjf package.tar.bz2 just-a-calendar
$ file package.tar.bz2
package.tar.bz2: bzip2 compressed data, block size = 900k
$ du -sh package.tar.bz2
76K     package.tar.bz2
```

Since we are specifying the file name here, which includes the `.bz2` part at the end, we can tell
`tar` to just figure out the compression we want to use. Instead of the `j` argument specifying the
compression, we'd put in `a` to indicate this.

```console
$ tar -caf package.tar.bz2 just-a-calendar
$ file package.tar.bz2
package.tar.bz2: bzip2 compressed data, block size = 900k
$ du -sh package.tar.bz2
76K     package.tar.bz2
```

### Exclude `.git` Directory

Now, the archive also contains the `.git` directory that was present in our clone. We probably don't
what that. The `tar` command provides `--exclude*` family of arguments to deal with this. For
example, as in our case, to ignore the folder `.git`, we could do:

```console
$ tar -caf package.tar.bz2 --exclude=.git just-a-calendar
$ du -sh package.tar.bz2
12K     package.tar.bz2
```

This package doesn't contain the `.git` folder (and consequently is *much* smaller). However, for
this particular problem, there's perhaps an even better solution, the `--exclude-vcs` argument. This
argument will ignore any VCS directories automatically and it knows about `.git`. So our command
becomes:

```console
$ tar -caf package.tar.bz2 --exclude-vcs just-a-calendar
```

Another similar useful argument is the `--eclude-backups`, which will **exclude backup and lock
files** which also is usually what we want.

### Set Initial Directory

The `-C` (or `--directory`) argument sets the initial working directory before creating the archive.
This will influence the paths with which the files *inside* the archive are saved with. This is
normally only useful if for some reason you can't `cd` or `pushd` to that directory yourself, which
is not very often.

## Inspecting Archives

The `-t` (or `--list`) can be used to list the contents of an archive without extracting it.

Additional options after `-t`:

1. `v` -- Verbose listing. The affect of adding this option is like adding `-l` to the `ls` command.
   That is, it will show each file's permissions, size, last modified *etc.* details.

1. `f` -- Treat next argument as the archive file name. This argument is *usually* always needed
   with the `-t` command (unless the archive is being piped in to the `tar -t` command).

Let's run this on our package archive created in the previous section.

```console
$ tar -tf package.tar.bz2 | wc -l
6
```

### Single vs Multiple Top Levels

There's one thing about extracting archives that's extremely annoying. If it contains multiple files
at top level, it'll pollute the current directory with several objects. To combat this, if we make
it a habit to create a new folder and extract inside it, it might turn out that the archive itself
contains a top level directory, so now we end up one useless directory in the tree.

This situation is actually handled very well by the `aunpack` command from the [atool][] script.
This command takes an archive (of any of several different formats) and extracts it. If it contains
a single top level entry, it is extracted to your working directory. If it contains several top
level entries, a new directory is created and the extraction happens inside that new directory. This
command is extremely convenient, for this and several other reasons.

To find out if an archive has a single top-level entry or multiple, the following snippet can be
used:

```sh
tar -tf package.tar.bz2 | cut -d/ -f1 | sort -u
```

This will print out one top-level entry per line. If there's only one line in the output, then
there's only one top-level. How this works is that first, the `cut` command splits the listing with
`/` character, the file separator and only prints the first entry, which will be the top level
entry. Then, the `sort` command will sort the top-levels and only print the **unique** entries
(that's what the `-u` is for). We could further pipe this to `wc -l` and check if it results in `1`.

## Extracting Archives

The `-x` (or `--extract`) command is used to **extract** the contents of archives.

This command takes the following arguments:

1. `v` -- Verbose logging. Prints each file path as it is being extracted.

1. `z` or `j` -- Specify the compression format, if needed. Similar in working as with the `-c`
   command.

1. `f` -- Reads the next argument as the archive file name. This is almost always used with this
   command to specify the archive to extract. If this is not provided, the archive content is
   expected to be available from standard input.

1. `k` (or `--keep-old-files`) -- Fail if any existing files will be overwritten by extracting. This
   is useful if you don't want any of your existing files to be overwritten.

So, to extract our archive (in a separate location, of course):

```console
$ mkdir spike && cd spike
$ tar -xaf ../package.tar.bz2
```

### Extracting to Different Directory

The extract command also supports the `-C` (or `--directory`) argument that sets the initial working
directory before extracting. This can be used to change the location where the extracted
files/folder will be saved.

## Transferring Archives / Directories

In this section, I'll show a couple of quick examples where we need to transfer a folder tree
between current local system and a remote system reachable by SSH.

### Local to Remote

We could create a `tar` file of the folder (and any other files as well), transfer the file to the
remote system, login to the remote system and unpack it there.

There's a couple of problems with this approach:

1. Since we are creating an archive of the folder on our local disk, we need to have the necessary
   free space for that archive. This may be less the size of the folder, but can still be
   significant if the folder is large. The same problem will also appear on the remote system.
1. We need write permissions on the local disk. If we want to just take a folder to a remote system,
   we should only need write permission on the remote disk, not on the local disk.

To avoid the above two problems, we can transfer the archive directly as a stream, without saving it
to the local disk. Notice that if we don't provide a filename for the create (`-c`) command, the
archive will be written to standard out. Similarly, if we don't provide a filename for the extract
(`-x`) command, it will read the archive from standard input. Our solution below will leverage these
two facts.

```sh
tar -cj just-a-calendar | ssh remote tar -xj
```

The first command (`tar -cj just-a-calendar`) creates a `bzip2`-compressed archive (we could've used
`z` here to use `gz` compression instead) and writes it to the standard out. This becomes the
standard input for the `ssh` command which will connect to the remote host, invoke the `tar -xj`
command, and forwards it's own standard input to that `tar -xj` command. The `tar -xj` command
extracts the archive from it's standard input, using `bzip2` for decompressing and writes the
extracted contents to the remote user's home directory.

For added measure, we could use the `-C` (or `--directory`) argument to `tar -xj` to set the
directory where the extracted files would be saved.

This method is extremely handy since the archive is not written to the disk anywhere, not on local,
not on remote. It's only processed as a stream of bytes.

The `-j` argument to the `tar` commands is not strictly necessary. The whole thing will work even
without it.  But since the archive is being transferred over network, it pays to spend a little
processor time into compressing it so as to minimize network usage (and consequently, speed up the
operation).

We could've added the `-v` argument to one (or both!?) `tar` commands to show the files as they are
being archived/extracted.

### Remote to Local

This follows a similar method as in the previous section, but in the other way around. We run the
archiver `tar` command on the remote host, and the extractor `tar` command on the local machine.

```sh
ssh remote tar -cj just-a-calendar | tar -xj
```

This will recreate the `just-a-calendar` folder on the remote host, onto the local disk. We could
use the `-C` argument to either `tar` command to set it's initial working directory.

Of course, if wanted to just save the archive on the local disk, not extract it, we could just
redirect the stream to a file.

    ssh remote tar -cj just-a-calendar > package.tar.bz2

## Conclusion

The `tar` command, in all it's variations, is irreplaceable in it's utility for these kind of
purposes. The handiest resource for getting help while working with it is, of course, the man page.
But when we're in the mood to just copy-pasta (yes, pasta) a command to serve the purpose, I hope
this article will be helpful.


[atool]: https://www.nongnu.org/atool/
