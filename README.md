# Project Trellis DOT extract

Install the dependencies:
 - Python 3.5 or later, including development libraries (`python3-dev` on Ubuntu)
 - A modern C++14 compiler (Clang is recommended)
 - CMake 3.5 or later
 - Boost including boost-python
 
 
For a generic environment:

    source environment.sh

Optionally, modify `user_environment.sh` and rerun the above command if needed.

Build libtrellis:

    cd libtrellis
    cmake .
    make

# Generate graph
 - Run `extract_graph.py`.


### License

All code in the Project Trellis repository is licensed under the very permissive
[ISC Licence](COPYING). A copy can be found in the [`COPYING`](COPYING) file.

All new contributions must also be released under this license.
