use vergen_git2::{Emitter, Git2Builder};

fn main() {
    let git2 = Git2Builder::default()
        .sha(true)
        .dirty(true)
        .build()
        .expect("Failed to build git config");

    Emitter::default()
        .add_instructions(&git2)
        .expect("Failed to add git instructions")
        .emit()
        .expect("Failed to emit version info");
}
