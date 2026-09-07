#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

class BogoSortExaminer {
public:
    BogoSortExaminer(std::size_t item_count, std::size_t exam_size,
                     std::uint64_t start_seed)
        : item_count_(item_count), exam_size_(exam_size),
          start_seed_(start_seed) {
        if (item_count_ == 0) {
            throw std::invalid_argument("item_count must be at least 1");
        }
        if (exam_size_ == 0) {
            throw std::invalid_argument("exam_size must be at least 1");
        }
    }

    static std::uint64_t todayInJst() {
        const auto now = std::chrono::system_clock::now() + std::chrono::hours(9);
        const std::time_t time = std::chrono::system_clock::to_time_t(now);
        std::tm utc{};
#ifdef _WIN32
        gmtime_s(&utc, &time);
#else
        gmtime_r(&time, &utc);
#endif
        return static_cast<std::uint64_t>(utc.tm_year + 1900) * 10'000
             + static_cast<std::uint64_t>(utc.tm_mon + 1) * 100
             + static_cast<std::uint64_t>(utc.tm_mday);
    }

    void examine(std::size_t progress_interval = 10'000) {
        attempt_counts_.clear();
        percentile_attempts_.clear();

        std::random_device device;
        std::seed_seq device_seed{
            device(), device(), device(), device(),
            device(), device(), device(), device()
        };
        std::mt19937_64 seed_generator(device_seed);
        std::uniform_int_distribution<std::uint64_t> factor_distribution(1, 10);
        std::uint64_t seed = start_seed_;

        for (std::size_t index = 0; index < exam_size_; ++index) {
            if (progress_interval != 0 && index % progress_interval == 0) {
                std::cout << "examined: " << index << " seeds\r" << std::flush;
            }

            seed += static_cast<std::uint64_t>(index)
                  * factor_distribution(seed_generator);
            const std::size_t attempts = attemptsUntilSorted(seed);
            if (attempts >= attempt_counts_.size()) {
                attempt_counts_.resize(attempts + 1, 0);
            }
            ++attempt_counts_[attempts];
        }

        if (progress_interval != 0) {
            std::cout << "examined: " << exam_size_ << " seeds\n";
        }
    }

    void calculatePercentiles() {
        if (attempt_counts_.empty()) {
            throw std::logic_error("examine() must be called first");
        }

        percentile_attempts_.clear();
        percentile_attempts_.reserve(1'000);
        for (std::size_t step = 1; step <= 1'000; ++step) {
            percentile_attempts_.push_back(attemptsAtStep(step));
        }
    }

    void savePercentiles(const std::string& output_path) {
        ensurePercentilesCalculated();
        std::ofstream output(output_path);
        if (!output) {
            throw std::runtime_error("could not open output file: " + output_path);
        }

        output << std::fixed << std::setprecision(1);
        for (std::size_t step = 1; step <= percentile_attempts_.size(); ++step) {
            output << static_cast<double>(step) / 10.0 << "% "
                   << percentile_attempts_[step - 1] << '\n';
        }
    }

    void savePlotSvg(const std::string& output_path) {
        ensurePercentilesCalculated();
        constexpr double width = 900.0;
        constexpr double height = 600.0;
        constexpr double left = 85.0;
        constexpr double right = 30.0;
        constexpr double top = 55.0;
        constexpr double bottom = 70.0;
        const double plot_width = width - left - right;
        const double plot_height = height - top - bottom;
        const std::size_t maximum_attempts = percentile_attempts_.back();

        std::ofstream output(output_path);
        if (!output) {
            throw std::runtime_error("could not open plot file: " + output_path);
        }

        output << "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" "
                  "height=\"600\" viewBox=\"0 0 900 600\">\n"
               << "<rect width=\"100%\" height=\"100%\" fill=\"white\"/>\n"
               << "<g stroke=\"black\" fill=\"none\">"
               << "<path d=\"M " << left << ' ' << top << " V "
               << height - bottom << " H " << width - right << "\"/>\n"
               << "<polyline stroke=\"#1f77b4\" stroke-width=\"2\" points=\"";

        for (std::size_t index = 0; index < percentile_attempts_.size(); ++index) {
            const double x = left + plot_width * percentile_attempts_[index]
                                     / std::max<std::size_t>(maximum_attempts, 1);
            const double percentage = static_cast<double>(index + 1) / 10.0;
            const double y = height - bottom - plot_height * percentage / 100.0;
            output << x << ',' << y << ' ';
        }

        output << "\"/></g>\n"
               << "<g font-family=\"sans-serif\" fill=\"black\" text-anchor=\"middle\">\n"
               << "<text x=\"450\" y=\"30\" font-size=\"20\">"
               << "possibility of succeeding in bogo-sort (N=" << item_count_
               << ")</text>\n"
               << "<text x=\"477\" y=\"585\">number of attempts</text>\n"
               << "<text transform=\"translate(20 300) rotate(-90)\">"
                  "possibility (%)</text>\n"
               << "<text x=\"85\" y=\"550\">0</text>\n"
               << "<text x=\"870\" y=\"550\">" << maximum_attempts << "</text>\n"
               << "<text x=\"65\" y=\"535\">0</text>\n"
               << "<text x=\"60\" y=\"65\">100</text>\n"
               << "</g>\n</svg>\n";
    }

    void run(const std::string& output_path, const std::string& plot_path,
             std::size_t progress_interval = 10'000) {
        examine(progress_interval);
        calculatePercentiles();
        savePercentiles(output_path);
        savePlotSvg(plot_path);
    }

private:
    std::size_t attemptsUntilSorted(std::uint64_t seed) const {
        std::vector<std::size_t> values(item_count_);
        std::iota(values.begin(), values.end(), 0);
        std::mt19937_64 generator(seed);
        std::size_t attempts = 0;

        do {
            std::shuffle(values.begin(), values.end(), generator);
            ++attempts;
        } while (!std::is_sorted(values.begin(), values.end()));
        return attempts;
    }

    std::size_t attemptsAtStep(std::size_t step) const {
        const std::size_t target = (step * exam_size_ + 999) / 1'000;
        std::size_t cumulative_count = 0;
        for (std::size_t attempts = 0; attempts < attempt_counts_.size(); ++attempts) {
            cumulative_count += attempt_counts_[attempts];
            if (cumulative_count >= target) {
                return attempts;
            }
        }
        throw std::logic_error("examination results are incomplete");
    }

    void ensurePercentilesCalculated() {
        if (percentile_attempts_.empty()) {
            calculatePercentiles();
        }
    }

    std::size_t item_count_;
    std::size_t exam_size_;
    std::uint64_t start_seed_;
    std::vector<std::size_t> attempt_counts_;
    std::vector<std::size_t> percentile_attempts_;
};

int main() {
    const std::size_t item_count = 6;
    const std::size_t exam_size = 1'000'000;
    const std::uint64_t start_seed = 2026;  // Or BogoSortExaminer::todayInJst().
    const std::size_t progress_interval = 10'000;
    const std::string output_path = "exam_data.txt";
    const std::string plot_path = "exam_plot.svg";

    try {
        BogoSortExaminer examiner(item_count, exam_size, start_seed);
        examiner.run(output_path, plot_path, progress_interval);
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
